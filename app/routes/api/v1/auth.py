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

# from app.utils.mailer_module import mail, template
from app.Config import ENV_PROJECT

# from app.schema.password import SetPassword
from typing import Optional
from app.schema.enums import UserTypeEnum


router = APIRouter()


class TenantID(BaseModel):
    tenant_id: Optional[str] = None
    tenant_email: Optional[str] = None


class Email_Body(BaseModel):
    email: str


@router.post("/login", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    user_type: UserTypeEnum,
    creds: OAuth2PasswordRequestForm = Depends(),
):
    user = None
    if user_type == "admin":
        user = {"_id": "", "password": ENV_PROJECT.ADMIN_PASSWORD}

    if hashing.verify_hash(creds.password, user["password"]):
        print("i am in hashing if statement")
        token_data = TokenData(
            user_id=user["_id"], user_type=user_type.value, scope="login"
        )
        token_generated = await create_access_token(token_data)
        set_cookies(response, token_generated.access_token, token_generated.refresh_token)
        return {"ok": True}
    print("i am not in hashing if statement")

    raise http_exception.CredentialsInvalidException()


@router.post("/refresh", response_class=ORJSONResponse, status_code=status.HTTP_200_OK)
async def token_refresh(
    response: Response, refresh_token: str = Depends(get_refresh_token)
):
    token_generated = await get_new_access_token(refresh_token)
    set_cookies(response, token_generated.access_token, token_generated.refresh_token)
    return {"ok": True}

