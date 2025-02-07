from app.Config import ENV_PROJECT
from app.database.models.Chemist import Chemist, ChemistDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class ChemistRepo(BaseMongoDbCrud[ChemistDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Chemist", unique_attributes=["email"]
        )

    async def new(self, sub: Chemist):
        return await self.save(
            ChemistDB(**sub.model_dump())
        )

chemist_repo = ChemistRepo()
