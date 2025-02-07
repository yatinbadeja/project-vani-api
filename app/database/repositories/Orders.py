from app.Config import ENV_PROJECT
from app.database.models.Orders import Orders, OrdersDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class OrdersRepo(BaseMongoDbCrud[OrdersDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Orders", unique_attributes=[]
        )

    async def new(self, sub: Orders):
        return await self.save(
            OrdersDB(**sub.model_dump())
        )

orders_repo = OrdersRepo()
