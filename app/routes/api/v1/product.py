from fastapi import APIRouter, Depends, status, Response, Header
from fastapi.responses import ORJSONResponse
from app.Config import ENV_PROJECT
from loguru import logger
import app.http_exception as http_exception
from app.schema.token import TokenData
import app.http_exception as http_exception
from app.oauth2 import get_current_user
from fastapi import Query
from app.schema.token import TokenData
from app.database.repositories.crud.base import SortingOrder, Sort, Page, PageRequest

from app.database.models.Product import ProductCreate
from app.database.repositories.Product import product_repo
from app.database.models.Product import product


Product = APIRouter()


@Product.post(
    "/create/product", response_class=ORJSONResponse, status_code=status.HTTP_200_OK
)
async def createProduct(
    product_: ProductCreate,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()

    product__ = product_.model_dump()
    await product_repo.new(product(**product__))

    return {"success": True, "message": "Product Created Successfully"}


@Product.get(
    "/get/product/{product_id}",
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def getProduct(
    product_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()

    product = await product_repo.findOne(
        {"_id": product_id}, {"created_at": 0, "updated_at": 0}
    )
    if not product:
        raise http_exception

    return {"success": True, "data": product}


@Product.delete(
    "/delete/product/{product_id}",
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def deleteProduct(
    product_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()

    product = await product_repo.findOne({"_id": product_id})
    if not product:
        raise http_exception.NotFoundException(detail="Product Not Found")

    await product_repo.deleteById(product_id)

    return {"success": True, "message": "Product Deleted Successfully"}


@Product.put(
    "/update/product/{product_id}",
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def updateProduct(
    current_user: TokenData = Depends(get_current_user),
    product: ProductCreate = None,
    product_id: str = "",
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()

    productExists = await product_repo.findOne({"_id": product_id})
    if productExists is None:
        raise http_exception.ResourceNotFoundException()

    updated_dict = {k: v for k, v in product.dict().items() if v not in [None, ""]}

    await product_repo.update_one({"_id": product_id}, {"$set": updated_dict})

    return {
        "success": True,
        "message": "Product Updated Successfully",
    }


@Product.get(
    "/view/all/product", response_class=ORJSONResponse, status_code=status.HTTP_200_OK
)
async def view_all_product(
    current_user: TokenData = Depends(get_current_user),
    search: str = None,
    category: str = None,
    page_no: int = Query(1, ge=1),
    limit: int = Query(12, le=24),
    sortField: str = "created_at",
    sortOrder: SortingOrder = SortingOrder.DESC,
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()

    page = Page(page=page_no, limit=limit)
    sort = Sort(sort_field=sortField, sort_order=sortOrder)
    page_request = PageRequest(paging=page, sorting=sort)

    result = await product_repo.viewAllProduct(
        search=search, category=category, pagination=page_request, sort=sort
    )

    return {"success": True, "message": "Data Fetched Successfully...", "data": result}


@Product.get(
    "/view/all/categories", response_class=ORJSONResponse, status_code=status.HTTP_200_OK
)
async def view_all_categories(
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()

    unique_categories_pipeline = [
        {"$group": {"_id": "$category"}},
        {"$project": {"_id": 1, "category": "$_id"}},
        {"$sort": {"category": 1}},
    ]
    categories_res = [
        doc async for doc in product_repo.collection.aggregate(unique_categories_pipeline)
    ]
    unique_categories = [entry["category"] for entry in categories_res]

    return {"success": True, "message": "Data Fetched Successfully...", "data": unique_categories}


@Product.get(
    "/view/products/with_id",
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def getProducts(
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()

    products = await product_repo.collection.aggregate(
        [
            {
                "$project": {
                    "storage_requirement": 0,
                    "no_of_tablets_per_pack": 0,
                    "category": 0,
                    "state": 0,
                    "expiry_date": 0,
                    "description": 0,
                    "created_at": 0,
                    "updated_at": 0,
                }
            }
        ]
    ).to_list(None)
    return {"success": True, "data": products}
