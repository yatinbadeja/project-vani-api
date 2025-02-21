
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

    
