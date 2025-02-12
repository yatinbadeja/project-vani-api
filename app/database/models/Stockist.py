from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict
from app.database.models.entity import Name,Address,phoneNumber
from app.schema.enums import UserRole
from typing import Optional

class Stockist(BaseModel):
    user_id: str
    name: Name
    company_name: str
    address: Address
    phone_number: phoneNumber

class StockistDB(Stockist):
    stockist_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))


class StockistCreate(BaseModel):
    name: Name
    company_name: str
    address: Address
    phone_number: phoneNumber
