from app.Config import ENV_PROJECT
from app.database.models.Stockist import Stockist, StockistDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class StockistRepo(BaseMongoDbCrud[StockistDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Stockist", unique_attributes=[]
        )

    async def new(self, sub: Stockist):
        return await self.save(
            StockistDB(**sub.model_dump())
        )

stockist_repo = StockistRepo()
