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
from app.database.models.Orders import OrderStatus
from app.database.models.Sale_Details import SaleDetails, SalesProduct, SaleDetailsDB
from app.database.models.Sales import Sales, SalesDB
from app.database.models.Stock_Movement import StockMovement, StockMovementDB
from app.database.models.Product_Stock import ProductStock, ProductStockDB
from app.database.repositories.Sales import sales_repo
from app.database.repositories.Sale_Details import sale_details_repo
from app.database.repositories.Stock_Movement import stock_movement_repo
from app.schema.enums import StockMovementTypeEnum
from fastapi import Query
from uuid import uuid4
from pymongo import UpdateOne
from typing import List
from app.database.repositories.crud.base import (
    PageRequest,
    SortingOrder,
    Sort,
    Page,
)

sales = APIRouter()


@sales.post(
    "/create",
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def createSales(
    salesProduct: SalesProduct,
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type != "admin" and current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()

    # 1. Create Sale record
    sale = Sales(
        chemist_id=current_user.user_id,
        customer_id=str(uuid4()),
        amount=salesProduct.quantity * salesProduct.unit_price,
    )
    newSales = await sales_repo.new(sale)

    if isinstance(newSales, dict):
        newSales = SalesDB.parse_obj(newSales)

    print("newSales", newSales)

    # 2. Create Sale Details record
    salesDetails = SaleDetails(
        sale_id=newSales.sale_id,
        product_id=salesProduct.product_id,
        quantity=salesProduct.quantity,
        unit_price=salesProduct.unit_price,
    )
    newSalesDetails = await sale_details_repo.new(salesDetails)
    print("newSalesDetails", newSalesDetails)

    # 3. Create Stock Movement (OUT)
    stock_movement = StockMovement(
        product_id=salesProduct.product_id,
        quantity=salesProduct.quantity,
        movement_type=StockMovementTypeEnum.OUT,
        chemist_id=current_user.user_id,
        unit_price=salesProduct.unit_price,
    )
    newStockMovement = await stock_movement_repo.new(stock_movement)
    print("newStockMovement", newStockMovement)

    # 4. Update Product Stock (decrease available quantity)
    product_stock = await product_stock_repo.get_product_stock(
        product_id=salesProduct.product_id, chemist_id=current_user.user_id
    )

    if isinstance(product_stock, dict):
        product_stock = ProductStockDB.parse_obj(product_stock)

    if not product_stock or product_stock.available_quantity < salesProduct.quantity:
        raise http_exception(status_code=400, detail="Insufficient stock available")

    product_stock.available_quantity -= salesProduct.quantity
    update_operation = UpdateOne(
        {"product_id": salesProduct.product_id, "chemist_id": current_user.user_id},
        {"$set": {"available_quantity": product_stock.available_quantity}},
    )

    operations = [update_operation]
    result = await product_stock_repo.bulk_write(operations)
    print("reults", result)

    return {"sale_id": newSales.sale_id, "message": "Sale created successfully"}


@sales.post(
    "/create/mulitple_sales",
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def createMulitpleSales(
    salesProducts: List[SalesProduct],  # Now accepting a list of SalesProduct
    current_user: TokenData = Depends(get_current_user),
):
    if current_user.user_type not in ["admin", "user"]:
        raise http_exception.CredentialsInvalidException()

    # Initialize the lists for bulk operations
    sales_operations = []
    sale_details_operations = []
    stock_movement_operations = []
    stock_update_operations = []

    # Process each sales product
    for salesProduct in salesProducts:
        # 1. Check Product Stock available quantity
        product_stock = await product_stock_repo.get_product_stock(
            product_id=salesProduct.product_id, chemist_id=current_user.user_id
        )

        if isinstance(product_stock, dict):
            product_stock = ProductStockDB.parse_obj(product_stock)

        if not product_stock or product_stock.available_quantity < salesProduct.quantity:
            raise http_exception(status_code=400, detail="Insufficient stock available")

        # 2. Create Sale record for each SalesProduct
        sale = Sales(
            chemist_id=current_user.user_id,
            customer_id=str(uuid4()),  # Assuming customer_id is generated here
            amount=salesProduct.quantity * salesProduct.unit_price,
        )
        newSales = await sales_repo.new(sale)

        # Add Sale operation to the list
        sales_operations.append(newSales)

        if isinstance(newSales, dict):
            newSales = SalesDB.parse_obj(newSales)

        # 3. Create Sale Details record for each SalesProduct
        salesDetails = SaleDetails(
            sale_id=newSales.sale_id,
            product_id=salesProduct.product_id,
            quantity=salesProduct.quantity,
            unit_price=salesProduct.unit_price,
        )
        newSalesDetails = await sale_details_repo.new(salesDetails)

        # Add Sale Details operation to the list
        sale_details_operations.append(newSalesDetails)

        # 4. Create Stock Movement (OUT) for each SalesProduct
        stock_movement = StockMovement(
            product_id=salesProduct.product_id,
            quantity=salesProduct.quantity,
            movement_type=StockMovementTypeEnum.OUT,
            chemist_id=current_user.user_id,
            unit_price=salesProduct.unit_price,
        )
        newStockMovement = await stock_movement_repo.new(stock_movement)

        # Add Stock Movement operation to the list
        stock_movement_operations.append(newStockMovement)

        # 5. Update Product Stock (decrease available quantity)
        product_stock.available_quantity -= salesProduct.quantity

        # Create the UpdateOne operation for stock update
        update_operation = UpdateOne(
            {
                "product_id": salesProduct.product_id,
                "chemist_id": current_user.user_id,
            },  # Filter
            {
                "$set": {"available_quantity": product_stock.available_quantity}
            },  # Update available_quantity
        )

        # Add the stock update operation to the list
        stock_update_operations.append(update_operation)

    # 5. Perform the bulk write operations
    if stock_update_operations:
        await product_stock_repo.bulk_write(stock_update_operations)  # Bulk update stock

    return {
        "message": "Sales created successfully",
        "success": True,
        "sale_ids": [sale.sale_id for sale in sales_operations],
    }


@sales.get("/", response_class=ORJSONResponse)
async def getAllSales(
    current_user: TokenData = Depends(get_current_user),
    search: str = None,
    category: str = None,
    state: str = None,
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

    result = await sales_repo.get_all_sales(
        current_user_id=current_user.user_id,
        search=search,
        category=category,
        state=state,
        pagination=page_request,
        sort=sort,
    )

    if result is None:
        raise http_exception.ResourceNotFoundException()

    return {"success": True, "message": "Data Fetched Successfully...", "data": result}
