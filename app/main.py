import time

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import Response

from app.Config import ENV_PROJECT
from app.core.app_configure import (
    configure_database,
    configure_logging,
    configure_middleware,
)
from app.database import mongodb
from app.http_exception import http_error_handler
from app.routes.api.routers import routers
from app.schema.health import Health_Schema
from app.utils.uptime import getUptime

start_time = time.time()


app = FastAPI(
    title=ENV_PROJECT.APP_TITILE,
    description=ENV_PROJECT.APP_DESCRIPTION,
    version="v" + ENV_PROJECT.APP_VERSION,
)


configs = [
    configure_database,
    configure_logging,
    configure_middleware,
]


@app.get(
    "/health",
    response_class=ORJSONResponse,
    response_model=Health_Schema,
    status_code=status.HTTP_200_OK,
    tags=["Health Route"],
)
async def check_health(request: Request, response: Response):
    """
    Health Route : Returns App details.

    """
    try:
        await mongodb.client.admin.command("ping")
        database_connected = True
    except:
        database_connected = False
    return Health_Schema(
        success=True,
        status=status.HTTP_200_OK,
        app=ENV_PROJECT.APP_TITILE,
        version=ENV_PROJECT.APP_VERSION,
        ip_address=request.client.host,
        mode=ENV_PROJECT.ENV,
        uptime=getUptime(start_time),
        database_connected=database_connected,
    )


for app_configure in configs:
    app_configure(app)


app.include_router(routers)
app.add_exception_handler(HTTPException, http_error_handler)
