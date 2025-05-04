from fastapi import APIRouter

from app.Config import ENV_PROJECT
from app.routes.api.v1.auth import auth as auth_endpoints
from app.routes.api.v1.admin import admin as admin_endponits
from app.routes.api.v1.product import Product as product_endpoints
from app.routes.api.v1.inventory import inventory as inventory_endpoints
from app.routes.api.v1.orders import OrdersRouter as orders_endpoints
from app.routes.api.v1.extraction import extraction as extraction_endpoints
from app.routes.api.v1.product_stock import product_Stock as product_Stock_endpoints
from app.routes.api.v1.stock_movement import stock_movement as stock_movement_endpoints
from app.routes.api.v1.sales import sales as sales_endpoints
from app.routes.api.v1.analytics import Analytics as analytics_endpoints

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

routers.include_router(
    extraction_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/extraction", tags=["Extraction"]
)

routers.include_router(
    product_Stock_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/product_stock", tags=["Product Stock"],
)

routers.include_router(
    stock_movement_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/stock_movement", tags=["Stock Movement"],
)

routers.include_router(
    sales_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/sales", tags=["Sales"],
)   

routers.include_router(
    analytics_endpoints, prefix=ENV_PROJECT.BASE_API_V1 + "/analytics", tags=["Analytics"],
)   
