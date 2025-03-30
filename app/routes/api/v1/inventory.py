from app.database.models.Inventory import InventoryCreate, Inventory, InventoryDB
from app.database.repositories.Inventory import inventory_repo
from fastapi import APIRouter, status, Depends
from fastapi.responses import ORJSONResponse
from app.schema.token import TokenData
from app.oauth2 import get_current_user
import app.http_exception as http_exception
from app.database.repositories.Chemist import chemist_repo
from app.database.repositories.Product import product_repo
from app.database.models.Orders import OrderStatus
from fastapi import Query
from app.database.repositories.crud.base import (
    PageRequest,
    Meta,
    PaginatedResponse,
    SortingOrder,
    Sort,
    Page,
)

inventory = APIRouter()


@inventory.post(
    "/create/chemist/inventory", response_class=ORJSONResponse, status_code=status.HTTP_200_OK
)
async def createChemistInventory(
    inventory: InventoryCreate,
    current_user: TokenData = Depends(get_current_user),
):

    if current_user.user_type not in ["admin", "user"]:
        raise http_exception.CredentialsInvalidException()

    chemistExists = await chemist_repo.findOne({
        "_id": inventory.chemist_id
    })
    if chemistExists is None:
        raise http_exception.ResourceNotFoundException()

    productExists = await product_repo.findOne({
        "_id": inventory.product_id
    })
    if productExists is None:
        raise http_exception.ResourceNotFoundException()

    await inventory_repo.new(Inventory(**inventory.model_dump()))

    return {
        "success": True,
        "message": "Product added to inventory successfully"
    }


@inventory.get("/inventory/product", response_class=ORJSONResponse)
async def chemistProduct(
    current_user: TokenData = Depends(get_current_user),
    chemist_id: str = "",
    product_id: str = ""
):
    if current_user.user_type not in ["admin", "user"]:
        raise http_exception.CredentialsInvalidException()

    if chemist_id not in ["", None]:
        chemistExists = await chemist_repo.findOne({
            "_id": chemist_id
        })
        if chemistExists is None:
            raise http_exception.ResourceNotFoundException()

    if product_id not in ["", None]:
        productExists = await product_repo.findOne({
            "_id": product_id
        })
        if productExists is None:
            raise http_exception.ResourceNotFoundException()

    matchDict = {}

    if chemist_id not in ["", None]:
        matchDict["chemist_id"] = chemist_id

    if product_id not in ["", None]:
        matchDict["product_id"] = product_id

    pipeline = []

    pipeline = [
        {
            "$match": matchDict
        },
        {
            '$lookup': {
                "from": "Product",
                "localField": "product_id",
                "foreignField": "_id",
                "as": "product"
            }
        },
        {
            '$lookup': {
                "from": "Chemist",
                "localField": "chemist_id",
                "foreignField": "_id",
                "as": "Chemist"
            }
        },
        {
            "$project": {
                "created_at": 0,
                "updated_at": 0
            }
        },
        {
            "$set": {
                "product": {"$ifNull": [{'$arrayElemAt': ['$product', 0]}, None]},
                "Chemist": {"$ifNull": [{'$arrayElemAt': ['$Chemist', 0]}, None]}
            }
        },
        {
            "$project": {
                "created_at": 0,
                "updated_at": 0,
                "product.created_at": 0,
                "product.updated_at": 0,
                "Chemist.created_at": 0,
                "Chemist.updated_at": 0,
                "Chemist.licence_number": 0
            }
        },
    ]
    print(pipeline)
    response = await inventory_repo.collection.aggregate(pipeline=pipeline).to_list(None)
    return {
        "success": True,
        "message": "Data Fetched Successfully",
        "data": response
    }


@inventory.get("/warehouse", response_class=ORJSONResponse)
async def chemistProducts(
    current_user: TokenData = Depends(get_current_user),
    search: str = None,
    category: str = None,
    page_no: int = Query(1, ge=1),
    limit: int = Query(12, le=24),
    sortField: str = "created_at",
    sortOrder: SortingOrder = SortingOrder.DESC,
):
    if current_user.user_type not in ["admin", "user"]:
        raise http_exception.CredentialsInvalidException()

    page = Page(page=page_no, limit=limit)
    sort = Sort(sort_field=sortField, sort_order=sortOrder)
    page_request = PageRequest(paging=page, sorting=sort)

    pipeline = []
    pipeline = [
        {
            "$match": {
                "user_id": current_user.user_id
            }
        },
        {
            "$lookup": {
                "from": "Orders",
                "localField": "_id",
                "foreignField": "chemist_id",
                "as": "ordersList",
                "pipeline": [
                    {
                        "$match": {
                            "status": OrderStatus.SHIPPED
                        }
                    }
                ]
            }
        },
        {
            "$lookup": {
                "from": "OrderDetails",
                "localField": "ordersList._id",
                "foreignField": "order_id",
                "as": "orderDetailsList"
            }
        },
        {
            "$unwind": "$orderDetailsList"
        },
        {
            "$unwind": "$orderDetailsList.product_details"
        },
        {
            "$group": {
                "_id": "$orderDetailsList.product_details.product_id",
                "quantity": {"$sum": "$orderDetailsList.product_details.quantity"},
                "purchasing_price": {
                    "$sum": {
                        "$multiply": ["$orderDetailsList.product_details.unit_price", "$orderDetailsList.product_details.quantity"]
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "Product",
                "localField": "_id",
                "foreignField": "_id",
                "as": "productDetails",
                "pipeline": [
                    {
                        "$project": {
                            "product_name": 1,
                            "category": 1,
                            "state": 1,
                            "measure_of_unit": 1,
                            "no_of_tablets_per_pack": 1,
                            "storage_requirement": 1,
                        }
                    }
                ]
            }
        },
        {
            "$unwind": "$productDetails"
        },
        {
            '$project': {
                "_id": 1,
                "quantity": 1,
                "purchasing_price": 1,
                "product_name": "$productDetails.product_name",
                "category": "$productDetails.category",
                "state": "$productDetails.state",
                "measure_of_unit": "$productDetails.measure_of_unit",
                "no_of_tablets_per_pack": "$productDetails.no_of_tablets_per_pack",
                "storage_requirement": "$productDetails.storage_requirement",
            }
        }
    ]

    if search:
        pipeline.append({
            "$match": {
                "$or": [
                    {"product_name": {"$regex": search, "$options": "i"}},
                    {"category": {"$regex": search, "$options": "i"}}
                ]
            }
        })

    if category:
        pipeline.append({
            "$match": {
                "category": category
            }
        })

    pipeline.append({
        "$sort": {sortField: 1 if sortOrder == SortingOrder.ASC else -1}
    })

    pipeline.append({
        "$skip": (page_no - 1) * limit
    })
    pipeline.append({
        "$limit": limit
    })

    data = await chemist_repo.collection.aggregate(pipeline=pipeline).to_list(None)

    # Get total count of matching records (without pagination)
    count_pipeline = pipeline.copy()
    count_pipeline.append({"$count": "total"})
    count_result = await chemist_repo.collection.aggregate(count_pipeline).to_list(None)
    total_count = count_result[0]["total"] if count_result else 0

    # Get unique categories
    category_pipeline = pipeline.copy()
    category_pipeline.append({
        "$group": {
            "_id": "$category"
        }
    })
    unique_categories_result = await chemist_repo.collection.aggregate(category_pipeline).to_list(None)
    unique_categories = [item["_id"] for item in unique_categories_result]

    # return {
    #     "message": "Inventory's warehouse details fetched successfully",
    #     "success": True,
    #     "data": data
    # }

    return PaginatedResponse(
        docs=data,
        meta=Meta(
            page=page_no,
            limit=limit,
            total=total_count,
            unique=unique_categories
        )
    )
