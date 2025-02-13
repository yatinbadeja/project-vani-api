from fastapi import FastAPI,status, Depends,File,UploadFile,Form
from fastapi.responses import ORJSONResponse
from fastapi import APIRouter
from app.schema.token import TokenData
from app.oauth2 import get_current_user
from app.schema.enums import UserRole
from app.database.models.common import Username
import app.http_exception as http_exception
from app.utils.mailer_module import mail
from app.database.models.user import User
from app.database.repositories.user import user_repo
from app.utils.generatePassword import generatePassword
from app.utils.hashing import hash_password
import re
from app.utils.cloudinary_client import cloudinary_client
from app.utils.mailer_module import template
from app.database.models.user import UserCreate
from app.database.repositories.crud.base import SortingOrder,Sort,Page,PageRequest
from fastapi import Query
from app.database.repositories.user import user_repo
from app.database.models.Stockist import StockistCreate
from app.database.models.Stockist import Stockist
from app.database.repositories.Stockist import stockist_repo
from app.database.repositories.Chemist import chemist_repo
from app.database.models.Chemist import Chemist,ChemistCreate
admin = APIRouter()

@admin.post('/create/user',response_class=ORJSONResponse,status_code=status.HTTP_200_OK)
async def create_user(
    user: UserCreate,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    userExists = await user_repo.findOne(
        {
            "email":user.email
        }
    )
    if userExists is not None:
        raise http_exception.ResourceNotFoundException()
    
    password = await generatePassword.createPassword()
    
    mail.send(
        "Welcome to DristiDocs",
        user.email,
        template.Onboard(role=user.role.value,email=user.email,password=password)
    )

    inserted_dict =  {}
    
    keys = ["password","email","role"]
    values = [hash_password(password=password),user.email,user.role.value]
    
    for k,v in zip(keys,values):
        inserted_dict[k] = v
        
    await user_repo.new(User(**inserted_dict))
    
    return {
        "success":True,
        "message":"User Inserted Successfully",
    }
    
@admin.get("/view/all/stockist",response_class=ORJSONResponse,status_code = status.HTTP_200_OK)
async def view_stockist_user(
    current_user : TokenData = Depends(get_current_user),
    search : str = None,
    page_no: int = Query(1, ge=1),
    limit: int = Query(10, le=20),
    sortField: str = "created_at",
    sortOrder: SortingOrder = SortingOrder.DESC,
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    page = Page(page=page_no, limit=limit)
    sort = Sort(sort_field=sortField, sort_order=sortOrder)
    page_request = PageRequest(paging=page, sorting=sort)
    
    result = await user_repo.viewAllStockist(search = search, pagination=page_request)
    
    return {
        "success":True,
        "message":"Data Fetched Successfully...",
        "data":result
    }
    
@admin.post('/create/stockist/{user_id}',response_class=ORJSONResponse,status_code=status.HTTP_200_OK)
async def create_stockist(
    user : StockistCreate,
    current_user : TokenData = Depends(get_current_user),
    user_id : str = "",
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    userExists = await user_repo.findOne({
        "_id":user_id,"role":"Stockist"
    })
    if userExists is None:
        raise http_exception.ResourceNotFoundException()
    
    accountExists = await stockist_repo.findOne({"user_id":user_id})
    if accountExists is not None:
        raise http_exception.ResourceConflictException()
    
    user = user.model_dump()
    user["user_id"] = user_id

    await stockist_repo.new(Stockist(**user))
    
    return {
        "success":True,
        "message":"Stockist Created Successfully",
    }
    
@admin.get("/view/all/chemist",response_class=ORJSONResponse,status_code = status.HTTP_200_OK)
async def view_chemist_user(
    current_user : TokenData = Depends(get_current_user),
    search : str = None,
    page_no: int = Query(1, ge=1),
    limit: int = Query(10, le=20),
    sortField: str = "created_at",
    sortOrder: SortingOrder = SortingOrder.DESC,
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    page = Page(page=page_no, limit=limit)
    sort = Sort(sort_field=sortField, sort_order=sortOrder)
    page_request = PageRequest(paging=page, sorting=sort)
    
    result = await user_repo.viewAllChemist(search = search, pagination=page_request)
    
    return {
        "success":True,
        "message":"Data Fetched Successfully...",
        "data":result
    }
    
@admin.post('/create/chemist/{user_id}',response_class=ORJSONResponse,status_code=status.HTTP_200_OK)
async def createChemistUser(
    user : ChemistCreate,
    current_user : TokenData = Depends(get_current_user),
    user_id : str = "",
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    userExists = await user_repo.findOne({
        "_id":user_id, "role":"Chemist"
    })
    if userExists is None:
        raise http_exception.ResourceNotFoundException()
    
    account_create = await chemist_repo.findOne({
        "user_id":user_id
    })
    if account_create is not None:
        raise http_exception.ResourceConflictException()
    
    user = user.model_dump()
    user["user_id"] = user_id
    await chemist_repo.new(Chemist(**user))
    
    return {
        "success":True,
        "message":"Chemist Created Successfully"
    }
    
@admin.put('/update/stockist/{user_id}',response_class=ORJSONResponse,status_code=status.HTTP_200_OK)
async def update_stockist(
    user : StockistCreate,
    current_user : TokenData = Depends(get_current_user),
    user_id : str = "",
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    userExists = await user_repo.findOne({
        "_id":user_id,"role":"Stockist"
    })
    if userExists is None:
        raise http_exception.ResourceNotFoundException()
    
    accountExists = await stockist_repo.findOne({"user_id":user_id})
    if accountExists is None:
        raise http_exception.ResourceNotFoundException()
    
    user = user.model_dump()

    updated_dict = {}
    
    updated_dict = {}

    for k, v in dict(user).items():
        if isinstance(v, str) and v not in ["", None]:
            updated_dict[k] = v
        elif isinstance(v, dict):
            temp_dict = {}  
            for k1, v1 in v.items():
                if isinstance(v1, str) and v1 not in ["", None]:
                    temp_dict[k1] = v1 

            if temp_dict:  #
                updated_dict[k] = temp_dict



    await stockist_repo.collection.update_one({"user_id":user_id},{"$set":updated_dict})
    
    return {
        "success":True,
        "message":"Stockist values updated successfully",
    }
    
@admin.put('/update/Chemist/{user_id}',response_class=ORJSONResponse,status_code=status.HTTP_200_OK)
async def update_chemist(
    user : ChemistCreate,
    current_user : TokenData = Depends(get_current_user),
    user_id : str = "",
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    userExists = await user_repo.findOne({
        "_id":user_id,"role":"Chemist"
    })
    if userExists is None:
        raise http_exception.ResourceNotFoundException()
    
    accountExists = await chemist_repo.findOne({"user_id":user_id})
    if accountExists is None:
        raise http_exception.ResourceNotFoundException()
    
    user = user.model_dump()

    updated_dict = {}
    
    for k, v in dict(user).items():
        if isinstance(v, str) and v not in ["", None]:
            updated_dict[k] = v
        elif isinstance(v, dict):
            temp_dict = {}  
            for k1, v1 in v.items():
                if isinstance(v1, str) and v1 not in ["", None]:
                    temp_dict[k1] = v1 

            if temp_dict:  
                updated_dict[k] = temp_dict
    await chemist_repo.collection.update_one({"user_id":user_id},{"$set":updated_dict})
    
    return {
        "success":True,
        "message":"Chemist values updated successfully",
    }



@admin.get('/get/chemist', response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def get_chemist(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    chemist_data = await chemist_repo.findOne({"user_id": user_id})
    if chemist_data is None:
        raise http_exception.ResourceNotFoundException()
    
    return {
        "success": True,
        "message": "Chemist data fetched successfully",
        "data": chemist_data
    }



@admin.get('/get/stockist', response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def get_stockist(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "admin":
        raise http_exception.CredentialsInvalidException()
    
    stockist_data = await stockist_repo.findOne({"user_id": user_id})
    if stockist_data is None:
        raise http_exception.ResourceNotFoundException()
    
    return {
        "success": True,
        "message": "Chemist data fetched successfully",
        "data": stockist_data
    }



