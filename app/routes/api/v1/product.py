from fastapi import APIRouter, Depends, status, Response, Header
from fastapi.responses import ORJSONResponse
from app.Config import ENV_PROJECT
from loguru import logger
import app.http_exception as http_exception
from app.schema.token import TokenData
import app.http_exception as http_exception
from app.oauth2 import get_current_user


from app.schema.token import TokenData

from app.database.models.Product import ProductCreate
from app.database.repositories.Product import product_repo
from app.database.models.Product import product


Product = APIRouter()

@Product.post("/create/product", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def createProduct(
    product_ : ProductCreate,
    current_user: TokenData = Depends(get_current_user),
) :
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    product__ = product_.model_dump()
    await product_repo.new(product(**product__))

    return {
        "success":True,
        "message":"Product Created Successfully"
    }

@Product.get("/get/product/{product_id}", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def getProduct(
    product_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    product = await product_repo.findOne({"_id":product_id},{"created_at":0,"updated_at":0})
    if not product:
        raise http_exception

    return {
        "success": True,
        "data": product
    }

@Product.delete("/delete/product/{product_id}", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def deleteProduct(
    product_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    product = await product_repo.findOne({"_id":product_id})
    if not product:
        raise http_exception.NotFoundException(detail="Product Not Found")

    await product_repo.deleteById(product_id)

    return {
        "success": True,
        "message": "Product Deleted Successfully"
    }
    
@Product.put("/update/product/{product_id}", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def updateProduct(
    current_user : TokenData = Depends(get_current_user),
    product: ProductCreate = None,
    product_id: str = "",
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    productExists = await product_repo.findOne({"_id":product_id})
    if productExists is None:
        raise http_exception.ResourceNotFoundException()
    
    updated_dict = {k:v for k,v in product.dict().items() if v not in [None,""]}
    
    await product_repo.update_one({"_id":product_id},{"$set":updated_dict})
    
    return {
        "success":True,
        "message":"Product Updated Successfully",
    }
    
@Product.get("/get/products", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def getProducts(
    current_user : TokenData = Depends(get_current_user),
):
    if current_user.user_type != "user" and current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    products = await product_repo.collection.aggregate([
        {
            "$project":{
                "created_at":0,
                "updated_at":0
            }
        }
    ]).to_list(None)
    return {
        "success":True,
        "data":products
    }
    

