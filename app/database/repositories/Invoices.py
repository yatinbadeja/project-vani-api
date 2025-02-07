from app.Config import ENV_PROJECT
from app.database.models.Invoices import Invoices, InvoicesDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class InvoicesRepo(BaseMongoDbCrud[InvoicesDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Invoices", unique_attributes=[]
        )

    async def new(self, sub: Invoices):
        return await self.save(
            InvoicesDB(**sub.model_dump())
        )

invoices_repo = InvoicesRepo()
