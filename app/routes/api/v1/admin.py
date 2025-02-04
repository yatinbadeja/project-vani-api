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
    
    keys = ["userName","password","email","role"]
    values = [user.userName,hash_password(password=password),user.email,user.role.value]
    
    for k,v in zip(keys,values):
        inserted_dict[k] = v
        
    await user_repo.new(User(**inserted_dict))
    
    return {
        "success":True,
        "message":"User Inserted Successfully",
    }
    
@admin.post("/test")
async def getTest(
    file: UploadFile = File(...)
):
    print(file=file)
    return cloudinary_client.upload_file(file=file)
    
    



