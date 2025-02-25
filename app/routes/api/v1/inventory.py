from app.database.models.Inventory import InventoryCreate,Inventory,InventoryDB
from app.database.repositories.Inventory import inventory_repo
from fastapi import APIRouter,status,Depends
from fastapi.responses import ORJSONResponse
from app.schema.token import TokenData
from app.oauth2 import get_current_user
import app.http_exception as http_exception
from app.database.repositories.Chemist import chemist_repo
from app.database.repositories.Product import product_repo

inventory = APIRouter()

@inventory.post(
    "/create/chemist/inventory",response_class=ORJSONResponse,status_code=status.HTTP_200_OK
)
async def createChemistInventory(
    inventory : InventoryCreate ,
    current_user : TokenData = Depends(get_current_user),
):
    
    if current_user.user_type not in ["admin","user"]:
        raise http_exception.CredentialsInvalidException()
    
    chemistExists = await chemist_repo.findOne({
        "_id":inventory.chemist_id
    })
    if chemistExists is None:
        raise http_exception.ResourceNotFoundException()
    
    productExists = await product_repo.findOne({
        "_id":inventory.product_id
    })
    if productExists is None:
        raise http_exception.ResourceNotFoundException()
    
    await inventory_repo.new(Inventory(**inventory.model_dump()))
    
    return {
        "success":True,
        "message":"Product added to inventory successfully"
    }
    
@inventory.get("/inventory/product",response_class=ORJSONResponse)
async def chemistProduct(
    current_user : TokenData = Depends(get_current_user),
    chemist_id : str = "",
    product_id : str = ""
):
    if current_user.user_type not in ["admin","user"]:
        raise http_exception.CredentialsInvalidException()
    
    if chemist_id not in ["",None]:
        chemistExists = await chemist_repo.findOne({
            "_id":chemist_id
        })
        if chemistExists is None:
            raise http_exception.ResourceNotFoundException()
    
    if product_id not in ["",None]:
        productExists = await product_repo.findOne({
            "_id":product_id
        })
        if productExists is None:
            raise http_exception.ResourceNotFoundException()
    
    matchDict = {}
    
    if chemist_id not in ["",None]:
        matchDict["chemist_id"]= chemist_id
        
    if product_id not in ["",None]:
        matchDict["product_id"] = product_id
        
    pipeline = []
    
    pipeline = [
        {
            "$match":matchDict
        },
        {
            '$lookup':{
                "from":"Product",
                "localField":"product_id",
                "foreignField":"_id",
                "as":"product"
            }
        },
        {
            '$lookup':{
                "from":"Chemist",
                "localField":"chemist_id",
                "foreignField":"_id",
                "as":"Chemist"
            }
        },
        {
            "$project":{
                "created_at":0,
                "updated_at":0
            }
        },
        {
            "$set":{
                "product":{"$ifNull":[{'$arrayElemAt': ['$product', 0]},None]},
                "Chemist":{"$ifNull":[{'$arrayElemAt': ['$Chemist', 0]},None]}
            }
        },
        {
            "$project":{
                "created_at":0,
                "updated_at":0,
                "product.created_at":0,
                "product.updated_at":0,
                "Chemist.created_at":0,
                "Chemist.updated_at":0,
                "Chemist.licence_number":0
            }
        },
    ]
    print(pipeline)
    response = await inventory_repo.collection.aggregate(pipeline=pipeline).to_list(None)
    return {
        "success":True,
        "message":"Data Fetched Successfully",
        "data":response
    }
    