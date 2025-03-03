from fastapi import APIRouter, BackgroundTasks, Depends, status, Response, Header
from fastapi.responses import ORJSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.Config import ENV_PROJECT
from loguru import logger
from pydantic import BaseModel
import app.http_exception as http_exception
from app.schema.token import TokenData
import app.http_exception as http_exception
from app.utils.hashing import verify_hash, hash_password
from app.oauth2 import get_current_user
from app.database.repositories.token import refresh_token_repo

# from app.database.connections.mongo import conn
from app.database import mongodb

# from app.database.repositories.token import refresh_token_repo
from app.oauth2 import (
    create_access_token,
    # create_forgot_password_access_token,
    # create_signup_access_token,
    get_new_access_token,
    # verify_forgot_password_access_token,
    # verify_signup_access_token,
    get_refresh_token,
    set_cookies,
)
from app.schema.token import TokenData
from app.utils import hashing
from app.database.repositories.user import user_repo
# from app.utils.mailer_module import mail, template
from app.Config import ENV_PROJECT

# from app.schema.password import SetPassword
from typing import Optional
from app.schema.enums import UserTypeEnum


auth = APIRouter()


class TenantID(BaseModel):
    tenant_id: Optional[str] = None
    tenant_email: Optional[str] = None


class Email_Body(BaseModel):
    email: str


@auth.post("/login", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    user_type: UserTypeEnum,
    creds: OAuth2PasswordRequestForm = Depends(),
):
    user = None
    if user_type == UserTypeEnum.ADMIN and creds.username == ENV_PROJECT.ADMIN_EMAIL:
        user = {
            "password": ENV_PROJECT.ADMIN_PASSWORD,
            "_id": "",
        }
    elif user_type in [
        UserTypeEnum.User
    ]:
        user = await user_repo.findOne(
                {"email": creds.username},
                {"_id", "password"},
            )

    if hashing.verify_hash(creds.password, user["password"]):
        print("i am in hashing if statement")
        token_data = TokenData(
            user_id=user["_id"], user_type=user_type.value, scope="login"
        )
        token_generated = await create_access_token(token_data)
        set_cookies(response, token_generated.access_token, token_generated.refresh_token)
        return {"ok": True, "accessToken":token_generated.access_token}
    print("i am not in hashing if statement")

    raise http_exception.CredentialsInvalidException()


@auth.get("/current/user", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def get_current_user_details(
    current_user: TokenData = Depends(get_current_user),
):
    user = await user_repo.findOne({"_id": current_user.user_id})
    if user is None:
        raise http_exception.ResourceNotFoundException()

    user_role = user["role"]

    pipeline = [
        {"$match": {"_id": current_user.user_id}},
        {
            "$lookup": {
                "from": user_role,
                "localField": "_id",
                "foreignField": "user_id",
                "as": "UserData",
            }
        },
        {
            "$set": {
                "UserData": {
                    "$cond": [
                        {"$eq": [{"$size": "$UserData"}, 0]},
                        None,
                        {"$arrayElemAt": ["$UserData", 0]},
                    ]
                }
            }
        },
        {
            "$project": {
                "password": 0,
                "created_at": 0,
                "updated_at": 0,
                "UserData._id": 0,
                "UserData.user_id": 0,
                "UserData.created_at": 0,
                "UserData.updated_at": 0,
            }
        },
    ]

    response = await user_repo.collection.aggregate(pipeline=pipeline).to_list(None)

    return {
        "success": True,
        "message": "User Profile Fetched Successfully",
        "data": response,
    }



@auth.post("/refresh", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def token_refresh(
    response: Response, refresh_token: str = Depends(get_refresh_token)
):
    token_generated = await get_new_access_token(refresh_token)
    set_cookies(response, token_generated.access_token, token_generated.refresh_token)
    return {"ok": True}

@auth.post("/logout", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def logout(response: Response, refresh_token: str = Depends(get_refresh_token)):
    await refresh_token_repo.deleteOne({"refresh_token": refresh_token})
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        max_age=0,
        secure=True,
        samesite="none",
    )
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        max_age=0,
        secure=True,
        samesite="none",
    )
    return {"ok": True}

