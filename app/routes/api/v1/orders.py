from typing import List, Optional, Dict, Union
from fastapi import APIRouter, status, Depends
from fastapi.responses import ORJSONResponse
from app.schema import token
from app.schema.token import TokenData
from app.database.models.Orders import OrderStatus,Orders1,OrdersCreate
from app.oauth2 import get_current_user
import app.http_exception as http_exception
from app.database.repositories.Stockist import stockist_repo
from app.database.repositories.Chemist import chemist_repo
from app.database.repositories.Orders import orders_repo
import datetime
from app.database.models.Order_Details import OrderDetails
from app.database.repositories.Order_Details import order_details_repo
import asyncio
from app.database.repositories.Product import product_repo
from app.database.models.Order_Details import Orders

OrdersRouter = APIRouter()


@OrdersRouter.post(
    "/create/user/orders", response_class=ORJSONResponse, status_code=status.HTTP_200_OK
)
async def createUserOrders(
    order: OrdersCreate,
    status: OrderStatus,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()

    stockistExists = await stockist_repo.findOne({"_id": order.stockist_id})
    if stockistExists is None:
        raise http_exception.ResourceNotFoundException()
    print('order', order)
    chemist = await chemist_repo.findOne({"user_id": current_user.user_id})

    date = datetime.datetime.strptime(order.order_date, "%Y-%m-%d")

    data = order.model_dump()
    data["order_date"] = date
    data["status"] = status.value
    data["chemist_id"] = chemist["_id"]
    response =  await orders_repo.new(Orders1(**data))
    print(response)
    return {
        "success":True,
        "message":"Data Inserted Successfully",
        "data":response.order_iD
    }
    
@OrdersRouter.get("/get/users/orders/{chemist_id}",response_class=ORJSONResponse)
async def getUserOrders(
    current_user: TokenData = Depends(get_current_user), chemist_id: str = ""
):
    if current_user.user_type != "admin" and current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()

    chemistExists = await chemist_repo.findOne({"_id": chemist_id})
    if chemistExists is None:
        raise http_exception.ResourceNotFoundException()

    pipeline = [
        {"$match": {"chemist_id": chemist_id}},
        {
            "$lookup": {
                "from": "Stockist",
                "localField": "stockist_id",
                "foreignField": "_id",
                "as": "Stockist",
            }
        },
        {"$set": {"Stockist": {"$arrayElemAt": ["$Stockist", 0]}}},
        {
            "$project": {
                "stockist_id": 0,
                "chemist_id": 0,
                "created_at": 0,
                "updated_at": 0,
                "Stockist.user_id": 0,
                "Stockist.created_at": 0,
                "Stockist.updated_at": 0,
            }
        },
    ]

    return {
        "message": "Data Fetched Succesfully",
        "success": True,
        "data": await orders_repo.collection.aggregate(pipeline=pipeline).to_list(None),
    }


@OrdersRouter.post(
    "/create/orders/details",
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def createOrdersDetails(
    orders_details: OrderDetails,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "admin" and current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()

    tasks = []
    tasks.append(orders_repo.findOne({"_id": orders_details.order_id}))

    for data in orders_details.model_dump()["product_details"]:
        for key, values in data.items():
            tasks.append(order_details_repo.findOne({"_id": key}))

    result = await asyncio.gather(*tasks)

    if None in result:
        http_exception.ResourceNotFoundException()

    orders_details = orders_details.model_dump()

    await order_details_repo.new(OrderDetails(**orders_details))

    return {
        "sucess": True,
        "message": "Data Inserted Successfully",
    }


@OrdersRouter.get(
    "/get/orders/details/{order_id}",
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def getOrdersDetails(
    order_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "admin" and current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()

    orderExists = await orders_repo.findOne({"_id": order_id})
    if orderExists is None:
        raise http_exception.ResourceNotFoundException()

    pipeline = [
        {"$match": {"order_id": order_id}},
        {"$unwind": "$product_details"},
        {
            "$lookup": {
                "from": "Product",
                "localField": "product_details.product_id",
                "foreignField": "_id",
                "as": "ProductDetails",
            }
        },
        {"$set": {"ProductDetails": {"$arrayElemAt": ["$ProductDetails", 0]}}},
        {
            "$project": {
                "created_at": 0,
                "updated_at": 0,
                "Stockist.user_id": 0,
                "ProductDetails.created_at": 0,
                "ProductDetails.updated_at": 0,
                "ProductDetails.description": 0,
                "ProductDetails.storage_requirement": 0,
            }
        },
    ]

    data = await stockist_repo.findOne({"_id": orderExists["stockist_id"]})
    response = await order_details_repo.collection.aggregate(pipeline=pipeline).to_list(
        None
    )

    return {
        "message": "Order Details updated successfully",
        "success": True,
        "data": {
            "stockist": {
                "name": data["name"],
                "company_name": data["company_name"],
                "address": data["address"],
                "phone_number": data["phone_number"],
            },
            "orders": response,
            "order_details": orderExists,
        },
    }


@OrdersRouter.put("/update/orders/{order_id}", response_class=ORJSONResponse)
async def updateOrder(
    order: OrdersCreate,
    status: OrderStatus,
    order_id: str = "",
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "admin" and current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()

    orderExists = await orders_repo.findOne({"_id": order_id})
    if orderExists is None:
        raise http_exception.ResourceNotFoundException()

    updatedDict = {}
    for key, values in dict(order.model_dump()).items():
        print(key, values)
        if values not in ["", None]:
            if key == "order_date":
                updatedDict["order_date"] = datetime.datetime.strptime(values, "%Y-%m-%d")
            else:
                updatedDict[key] = values

    updatedDict["status"] = status.value
    print(updatedDict)
    await orders_repo.update_one({"_id": order_id}, {"$set": updatedDict})

    return {"message": "Order Details updated successfully"}


@OrdersRouter.put("/update/orders/details/{order_id}", response_class=ORJSONResponse)
async def updateOrderDetails(
    products: List[Orders],
    order_id: str = "",
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "admin" and current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()

    orderDetailsExists = await order_details_repo.findOne({"order_id": order_id})
    if orderDetailsExists is None:
        raise http_exception.ResourceNotFoundException()

    tasks = []

    for pro in products:
        print(pro.model_dump())
        print(pro.product_id)
        tasks.append(product_repo.findOne({"_id": pro.product_id}))

    result = await asyncio.gather(*tasks)
    if None in result:
        raise http_exception.ResourceNotFoundException()
    data = [data.model_dump() for data in products]
    await order_details_repo.update_one(
        {"order_id": order_id}, {"$set": {"product_details": data}}
    )
    return {"message": "Order Details updated successfully", "success": True}
