from app.Config import ENV_PROJECT
from app.database.models.Payment import Payment, PaymentDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class PaymentRepo(BaseMongoDbCrud[PaymentDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "Payment", unique_attributes=[]
        )

    async def new(self, sub: Payment):
        return await self.save(
            PaymentDB(**sub.model_dump())
        )

payment_repo = PaymentRepo()
