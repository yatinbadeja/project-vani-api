from typing import Union, List,Optional
from pydantic import BaseModel, Field 
import datetime
from app.database.models.common import Username
from app.schema.enums import UserRole
from uuid import uuid4

class User(BaseModel):
    email : str 
    password : str
    role : Optional[UserRole] = UserRole.STOCKIST
    
class UserDB(User):
    id : str = Field(default_factory=lambda:str(uuid4()),alias="_id")
    created_at : datetime.datetime = Field(default_factory=lambda:datetime.datetime.now(datetime.timezone.utc))
    updated_at : datetime.datetime = Field(default_factory=lambda:datetime.datetime.now(datetime.timezone.utc))
    
class UserCreate(BaseModel):
    email : str 
    role : UserRole = UserRole.STOCKIST