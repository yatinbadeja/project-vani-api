from app.Config import ENV_PROJECT
from .crud.base_mongo_crud import BaseMongoDbCrud
from app.database.models.Sale_Details import SaleDetails, SaleDetailsDB

class SaleDetailsRepo(BaseMongoDbCrud):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "SaleDetails", unique_attributes=[]
        )

    async def new(self, sub:SaleDetails):
        return await self.save(
            SaleDetailsDB(**sub.model_dump())
        )

sale_details_repo = SaleDetailsRepo()