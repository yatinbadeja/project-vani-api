
from fastapi import APIRouter, Depends, status, Response, Header
from fastapi.responses import ORJSONResponse
from app.Config import ENV_PROJECT
from loguru import logger
import app.http_exception as http_exception
from app.schema.token import TokenData
import app.http_exception as http_exception
from app.oauth2 import get_current_user


from app.schema.token import Tok6enData

from app.database.models.Product import ProductCreate
from app.database.repositories.Product import product_repo
from app.database.models.Product import Product


chemist = APIRouter()

@chemist.post("/create/product", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def createProduct(
    product : ProductCreate,
    current_user: TokenData = Depends(get_current_user),
) :
    if current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()
    
    product = product.model_dump()
    await product_repo.new(Product(**product))

    return {
        "success":True,
        "message":"Product Created Successfully"
    }

## Get Product by ID API
@chemist.get("/get/product/{product_id}", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def getProduct(
    product_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()
    
    product = await product_repo.get_by_id(product_id)
    if not product:
        raise http_exception.NotFoundException(detail="Product Not Found")

    return {
        "success": True,
        "data": product
    }

## Get all products API
@chemist.get("/get/products", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def getAllProducts(
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()
    
    products = await product_repo.
    return {
        "success": True,
        "data": products
    }

## Update product API
@chemist.put("/update/product/{product_id}", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def updateProduct(
    product_id: str,
    updated_product: ProductCreate,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()
    
    existing_product = await product_repo.get_by_id(product_id)
    if not existing_product:
        raise http_exception.NotFoundException(detail="Product Not Found")

    updated_product_data = updated_product.model_dump()
    await product_repo.update(product_id, updated_product_data)

    return {
        "success": True,
        "message": "Product Updated Successfully"
    }


## Delete Product API
@chemist.delete("/delete/product/{product_id}", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def deleteProduct(
    product_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()
    
    product = await product_repo.get_by_id(product_id)
    if not product:
        raise http_exception.NotFoundException(detail="Product Not Found")

    await product_repo.delete(product_id)

    return {
        "success": True,
        "message": "Product Deleted Successfully"
    }
 
