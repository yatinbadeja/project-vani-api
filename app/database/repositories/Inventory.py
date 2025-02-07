from app.Config import ENV_PROJECT
from app.database.models.Inventory import Inventory, InventoryDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class InventoryRepo(BaseMongoDbCrud[InventoryDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Inventory", unique_attributes=["chemist_id", "product_id"]
        )

    async def new(self, sub: Inventory):
        return await self.save(
            InventoryDB(**sub.model_dump())
        )

inventory_repo = InventoryRepo()
