from fastapi import APIRouter,Depends
from fastapi import UploadFile, File
from app.database.repositories.extraction import extraction_tools
from app.routes.api.v1.orders import createUserOrders,createOrdersDetails
from app.database.models.Order_Details import OrderDetails,Orders
from app.schema.token import TokenData
import app.http_exception as http_exception
from app.oauth2 import get_current_user
from app.database.models.Orders import OrdersCreate
extraction = APIRouter()

@extraction.post("/file/upload")
async def upload_file(file: UploadFile = File(...)):
    response = await extraction_tools.text_extraction_for_scanned_and_selectable_file_for_json_format_through_gemini(file)
    return {
        "success": True,
        "message": "Data Extracted Successfully",
        "data": response
    }
    

@extraction.post("/extraction/save/database")
async def save_extracted_data_to_database(
        data: dict,
        current_user : TokenData = Depends(get_current_user)
    ):
    if current_user.user_type != "user":
        raise http_exception.CredentialsInvalidException()
    
    order_create_instance = OrdersCreate(
        stockist_id=data["stockist_id"],
        order_date=data["date"],
        total_amount=data["date"]
    )
    response = await createUserOrders(
        order=order_create_instance,
        status = "Pending",
        current_user = current_user
    )
    order_id = response["data"]
    
    order_Details = OrderDetails(
        order_id=order_id,
        product_details=[
            Orders(
                product_id=product["product_id"],
                quantity=product["quantity"],
                unit_price=product["rate"]
            ) for product in data["items"]
        ]
    )
    await createOrdersDetails(
        orders_details= order_Details,
        current_user = current_user
    )
    
    return {
        "success": True,
        "message": "Data Inserted Successfully",
        "data": response
    }
    
    
    
    
    
    



