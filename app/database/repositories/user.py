from app.Config import ENV_PROJECT
from app.database.models.user import User,UserDB
from .crud.base_mongo_crud import BaseMongoDbCrud

class userRepo(BaseMongoDbCrud[UserDB]):
    def __init__(self):
        super().__init__(
            ENV_PROJECT.MONGO_DATABASE, "User", unique_attributes=["email"]
        )
        
    async def new(self, sub: User):
        return await self.save(
            UserDB(**sub.model_dump())
        )

user_repo = userRepo()