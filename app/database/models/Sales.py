from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum

class Sales(BaseModel):
    chemist_id: str
    customer_id: str
    amount: float

class SalesDB(Sales):
    sale_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))