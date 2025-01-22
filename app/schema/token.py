from typing import Literal, Optional

from pydantic import BaseModel


class BaseToken(BaseModel):
    access_token: str
    refresh_token: str
    scope: str


class TokenData(BaseModel):
    user_id: str
    # email: str
    user_type: Literal["admin", "hr", "sales", "coach"] = "coach"
    scope: Literal["login", "forgot_password"] = "login"


class RefreshTokenPost(BaseModel):
    refresh_token: str


class OnlyRefreshToken(BaseModel):
    refresh_token: str
