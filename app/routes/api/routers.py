from fastapi import APIRouter

from app.Config import ENV_PROJECT
from app.routes.api.v1.auth import auth as auth_endpoints
from app.routes.api.v1.admin import admin as admin_endponits
from app.routes.api.v1.product import Product as product_endpoints
from app.routes.api.v1.inventory import inventory as inventory_endpoints
from app.routes.api.v1.orders import OrdersRouter as orders_endpoints

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
    product_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/product", tags=["Product"]
)

routers.include_router(
    inventory_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/inventory", tags=["Inventory"]
)

routers.include_router(
    orders_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/orders", tags=["Orders"]
)
