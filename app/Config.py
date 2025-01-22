from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: Optional[str] = "dev"
    DEBUG: Optional[bool] = False
    BASE_API_V1: Optional[str] = "/api/v1"
    APP_VERSION: Optional[str] = None
    APP_TITILE: Optional[str] = None
    APP_DESCRIPTION: Optional[str] = None
    MONGO_URI: str
    MONGO_DATABASE: str
    # SECRET_KEY: str
    EMAIL_ADDRESS: str
    EMAIL_PASSWORD: str
    EMAIL_SERVER: str
    FRONTEND_DOMAIN: str
    
    LOGIN_ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES: int
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_SECRET: str
    ACCESS_TOKEN_SECRET: str
    SIGNUP_TOKEN_SECRET: str
    FORGOT_PASSWORD_TOKEN_SECRET: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
   

    model_config = SettingsConfigDict(env_file=".env")


ENV_PROJECT = Settings()