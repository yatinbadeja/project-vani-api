from app.Config import ENV_PROJECT
from app.database.models.Product import Product, ProductDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class ProductRepo(BaseMongoDbCrud[ProductDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Product", unique_attributes=["product_name"]
        )

    async def new(self, sub: Product):
        return await self.save(
            ProductDB(**sub.model_dump())
        )

product_repo = ProductRepo()
