from app.database.models.Inventory import InventoryCreate, Inventory, InventoryDB
from app.database.repositories.Inventory import inventory_repo
from fastapi import APIRouter, status, Depends
from fastapi.responses import ORJSONResponse
from app.schema.token import TokenData
from app.oauth2 import get_current_user
import app.http_exception as http_exception
from app.database.repositories.Chemist import chemist_repo
from app.database.repositories.Product import product_repo
from app.database.repositories.Product_Stock import product_stock_repo
from app.database.repositories.Stock_Movement import stock_movement_repo
from app.database.models.Orders import OrderStatus
from fastapi import Query
from app.database.repositories.crud.base import (
    PageRequest,
    SortingOrder,
    Sort,
    Page,
)

stock_movement = APIRouter()


@stock_movement.get("/", response_class=ORJSONResponse)
async def getAllStockMovement(
    current_user: TokenData = Depends(get_current_user),
    search: str = None,
    category: str = None,
    state: str = None,
    startDate: str = None,
    endDate: str = None,
    movement_type: str = None,
    page_no: int = Query(1, ge=1),
    limit: int = Query(12, le=24),
    sortField: str = "created_at",
    sortOrder: SortingOrder = SortingOrder.DESC,
):
    if current_user.user_type not in ["admin", "user"]:
        raise http_exception.CredentialsInvalidException()

    page = Page(page=page_no, limit=limit)
    sort = Sort(sort_field=sortField, sort_order=sortOrder)
    page_request = PageRequest(paging=page, sorting=sort)

    result = await stock_movement_repo.get_all_Stock_movement(
        current_user_id=current_user.user_id,
        search=search,
        category=category,
        state=state,
        movement_type=movement_type,
        pagination=page_request,
        sort=sort,
        startDate=startDate,
        endDate=endDate,
    )

    if result is None:
        raise http_exception.ResourceNotFoundException()

    return {"success": True, "message": "Data Fetched Successfully...", "data": result}
