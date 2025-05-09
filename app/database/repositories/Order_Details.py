from app.Config import ENV_PROJECT
from app.database.models.Order_Details import OrderDetails, OrderDetailsDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class OrderDetailsRepo(BaseMongoDbCrud[OrderDetailsDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "OrderDetails", unique_attributes=[]
        )

    async def new(self, sub: OrderDetails):
        return await self.save(
            OrderDetailsDB(**sub.model_dump())
        )

    async def get_order_details(self,order_id:str):
        return await self.find_one({"order_id": order_id})

order_details_repo = OrderDetailsRepo()
