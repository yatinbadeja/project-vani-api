from typing import Callable

from fastapi import FastAPI
from loguru import logger

from app.database import mongodb


def create_start_app_handler(app: FastAPI) -> Callable:  # type: ignore

    @logger.catch
    async def start_app() -> None:
        try:
            await mongodb.client.admin.command("ping")
            logger.info("MongoDB Connected.")
        except Exception as e:
            raise e

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore

    @logger.catch
    async def stop_app() -> None:
        try:
            mongodb.client.close()
            logger.info("Closed MongoDB Connection")
        except Exception as e:
            raise e

    return stop_app
