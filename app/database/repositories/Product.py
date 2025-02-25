from app.Config import ENV_PROJECT
from app.database.models.Product import product, ProductDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class ProductRepo(BaseMongoDbCrud[ProductDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Product", unique_attributes=["product_name"]
        )

    async def new(self, sub: product):
        return await self.save(
            ProductDB(**sub.model_dump())
        )

product_repo = ProductRepo()
