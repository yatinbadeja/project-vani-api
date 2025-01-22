import datetime

from fastapi import Depends, status, Request, Response
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from jose import JWTError, jwt
import app.http_exception as http_exception
from app.Config import ENV_PROJECT
from app.database.models.token import RefreshTokenCreate
from app.database.repositories.token import refresh_token_repo
from app.schema.token import BaseToken, TokenData

from typing import Optional, Dict


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        access_token: str = request.cookies.get("access_token", "")
        refresh_token: str = request.cookies.get("refresh_token", "")

        if refresh_token:
            return {"access_token": access_token, "refresh_token": refresh_token}
        else:
            if self.auto_error:
                raise http_exception.CredentialsInvalidException()
            else:
                return None


oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl=ENV_PROJECT.BASE_API_V1 + "/auth/login",
    scheme_name="User Authentication",
)
# oauth2_scheme_user = OAuth2PasswordBearer(
#     tokenUrl=ENV_PROJECT.BASE_API_V1 + "/auth/tenant/login",
#     scheme_name="User Authentication",
# )


async def create_refresh_token(data: TokenData):
    to_encode = data.model_dump()
    expire = datetime.timedelta(
        minutes=ENV_PROJECT.REFRESH_TOKEN_EXPIRE_MINUTES
    ) + datetime.datetime.now(datetime.timezone.utc)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, ENV_PROJECT.REFRESH_TOKEN_SECRET, algorithm="HS256"
    )
    return encoded_jwt


async def verify_refresh_token(refresh_token: str) -> TokenData:
    try:
        payload = jwt.decode(
            refresh_token, ENV_PROJECT.REFRESH_TOKEN_SECRET, algorithms="HS256"
        )

        user_id: str = payload.get("user_id", None)
        user_type: str = payload.get("user_type", None)
        scope: str = payload.get("scope", None)
        if user_id is None or user_type is None or scope is None:
            raise http_exception.CredentialsInvalidException
        token_data = TokenData(user_id=user_id, user_type=user_type, scope=scope)
        return token_data
    except JWTError:
        raise http_exception.CredentialsInvalidException


async def create_access_token(
    data: TokenData, old_refresh_token: str = None
) -> BaseToken:
    to_encode = data.model_dump()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=ENV_PROJECT.LOGIN_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    access_token = jwt.encode(
        to_encode, ENV_PROJECT.ACCESS_TOKEN_SECRET, algorithm="HS256"
    )
    refresh_token = await create_refresh_token(data=data)
    refresh_token_data: RefreshTokenCreate = RefreshTokenCreate(
        refresh_token=refresh_token, user_id=data.user_id, user_type=data.user_type
    )
    if old_refresh_token is None:
        res = await refresh_token_repo.new(data=refresh_token_data)
    else:
        res = await refresh_token_repo.update_one(
            {"refresh_token": old_refresh_token, "user_id": data.user_id},
            {
                "$set": {
                    "refresh_token": refresh_token,
                    "updated_at": datetime.datetime.now(datetime.timezone.utc),
                }
            },
        )
        if res.matched_count == 0:
            raise http_exception.CredentialsInvalidException()
    if res:
        token: BaseToken = BaseToken(
            access_token=access_token, refresh_token=refresh_token, scope=data.scope
        )
        return token
    raise http_exception.InternalServerErrorException()


async def get_new_access_token(refresh_token: str):
    token_data = await verify_refresh_token(refresh_token)
    return await create_access_token(token_data, old_refresh_token=refresh_token)


# async def create_signup_access_token(data: TokenData):
#     to_encode = data.model_dump()
#     expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
#         minutes=ENV_PROJECT.EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES
#     )
#     to_encode.update({"exp": expire})
#     access_token = jwt.encode(
#         to_encode, ENV_PROJECT.SIGNUP_TOKEN_SECRET, algorithm="HS256"
#     )
#     return access_token


# async def verify_signup_access_token(token: str) -> TokenData:
#     try:
#         payload = jwt.decode(
#             token,
#             ENV_PROJECT.SIGNUP_TOKEN_SECRET,
#             algorithms=["HS256"],
#         )
#         id = payload.get("id", None)
#         type: str = payload.get("type", None)
#         scope: str = payload.get("scope", None)
#         if id is None or type is None or scope is None:
#             raise http_exception.TOKEN_CREDENTIALS_INVALID
#         token_data = TokenData(id=id, type=type, scope=scope)
#         if scope != "signup":
#             raise http_exception.OUT_OF_SCOPE_ACCESS_TOKEN
#         return token_data
#     except JWTError:
#         raise http_exception.TOKEN_CREDENTIALS_INVALID


async def create_forgot_password_access_token(data: TokenData):
    to_encode = data.model_dump()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=ENV_PROJECT.EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    access_token = jwt.encode(
        to_encode, ENV_PROJECT.FORGOT_PASSWORD_TOKEN_SECRET, algorithm="HS256"
    )
    return access_token


async def verify_forgot_password_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            ENV_PROJECT.FORGOT_PASSWORD_TOKEN_SECRET,
            algorithms=["HS256"],
        )
        user_id = payload.get("user_id", None)
        user_type: str = payload.get("user_type", None)
        scope: str = payload.get("scope", None)
        if user_id is None or user_type is None or scope != "forgot_password":
            raise http_exception.CredentialsInvalidException()
        token_data = TokenData(user_id=user_id, user_type=user_type, scope=scope)
        return token_data
    except JWTError:
        raise http_exception.CredentialsInvalidException()


async def verify_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, ENV_PROJECT.ACCESS_TOKEN_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id", None)
        user_type: str = payload.get("user_type", None)
        scope: str = payload.get("scope", None)
        if user_id is None or user_type is None or scope is None or scope != "login":
            raise http_exception.CredentialsInvalidException()
        token_data = TokenData(user_id=user_id, user_type=user_type, scope=scope)
        return token_data
    except JWTError:
        raise http_exception.CredentialsInvalidException()


async def get_current_user(
    tokens: dict = Depends(oauth2_scheme),
) -> TokenData:
    token: TokenData = await verify_access_token(tokens["access_token"])
    return token

    # tenant = await tenant_repo.findOneById(token.id)
    # if not tenant:
    #     raise http_exception.TOKEN_CREDENTIALS_INVALID
    # del tenant["password"]
    # return TenantOut(id=tenant["_id"], **tenant)


async def get_refresh_token(tokens: dict = Depends(oauth2_scheme)) -> str:
    return tokens["refresh_token"]


def set_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ENV_PROJECT.LOGIN_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        samesite="none",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=ENV_PROJECT.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        samesite="none",
    )
