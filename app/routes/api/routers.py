from fastapi import APIRouter

from app.Config import ENV_PROJECT
from app.routes.api.v1.auth import auth as auth_endpoints
from app.routes.api.v1.admin import admin as admin_endponits
from app.routes.api.v1.chemist import chemist as chemist_endpoints


# from app.routes.api.v1.sales import sales as sales_endpoints
routers = APIRouter()

routers.include_router(
    auth_endpoints,
    prefix=ENV_PROJECT.BASE_API_V1 + "/auth",
    tags=["Authentication"],
)
routers.include_router(
    admin_endponits, prefix=ENV_PROJECT.BASE_API_V1 + "/admin", tags=["Admin"]
)

routers.include_router(
    chemist_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/chemist", tags=["Chemist"]
)
