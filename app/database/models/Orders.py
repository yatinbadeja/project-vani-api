from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict

class OrderStatus(str, Enum):
    PENDING = "Pending"
    SHIPPED = "Shipped"
    CANCELLED = "Cancelled"

class Orders1(BaseModel):
    stockist_id: str
    chemist_id: str
    order_date: datetime.datetime
    status: OrderStatus
    total_amount: float

class OrdersDB(Orders1):
    order_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))


class OrdersCreate(BaseModel):
    stockist_id: str
    order_date: str
    total_amount: float
