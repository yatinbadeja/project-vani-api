import json
import logging
import time
import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger
from starlette.requests import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.Config import ENV_PROJECT
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.utils.logging import loguru_sink_serializer


def configure_middleware(app: FastAPI):
    """
    Configures fastapi middleware
    """
    # TODO make cors wildcard as per further need
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://dristidocs.vercel.app",
            "http://dristidocs.vercel.app",
            "http://localhost:5173",
            "https://localhost:5173",
            "http://localhost:3001",
            "https://localhost:3001",
            "http://localhost:3000",
            "https://localhost:3000",
            "https://dev.admin.kingdomofchess.com",
            "https://dev.sales.kingdomofchess.com",
            "https://dev.hr.kingdomofchess.com",
            "https://dev.coach.kingdomofchess.com",
            "https://admin.kingdomofchess.com",
            "https://sales.kingdomofchess.com",
            "https://hr.kingdomofchess.com",
            "https://coach.kingdomofchess.com",
            "https://koc-app-admin.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """
        Middleware to add response time HEADER to the response.
        Every response will have total time taken in millisecond for the API.
        """
        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = round(round((time.time() - start_time) * 1000, 2))
            response.headers["X-Process-Time"] = str(process_time) + " ms"
            logger.info("{0} took time {1} ms", request.url.path, process_time)
            return response
        except Exception as e:
            logger.error(traceback.print_exc())
            return ORJSONResponse(
                json.dumps(
                    {
                        "loc": [],
                        "msg": f"Internal Server Error: [{str(e)}]",
                        "type": "unexpected_error",
                    }
                ),
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            )


def configure_database(app: FastAPI):
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))


def configure_logging(app: FastAPI):
    """
    Configures logging
    """
    logger.remove()
    level_name = "DEBUG" if ENV_PROJECT.DEBUG else "INFO"
    logger.add(
        loguru_sink_serializer,
        level=level_name,
        enqueue=True,
        serialize=True,
    )
    logging.getLogger("passlib").setLevel(logging.ERROR)
    app.logger = logger
