from typing import List

from fastapi import status
from loguru import logger
from pymongo.errors import DuplicateKeyError

from app.Config import ENV_PROJECT
from app import http_exception

from ..models.token import RefreshTokenCreate, RefreshTokenDB
from .crud.base_mongo_crud import BaseMongoDbCrud


class RefreshTokenRepository(BaseMongoDbCrud[RefreshTokenDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "token", unique_attributes=["refresh_token"]
        )

    async def new(self, data: RefreshTokenCreate):
        data = RefreshTokenDB(**data.model_dump())
        try:
            res = await self.save(data)
            return res
        except DuplicateKeyError as e:
            logger.error(e)
            raise http_exception.ResourceConflictException()
        except Exception as e:
            print(e)
            logger.error(e)
            raise http_exception.InternalServerErrorException()


refresh_token_repo = RefreshTokenRepository()
