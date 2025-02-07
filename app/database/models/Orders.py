from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict
# Enum for Order Status
class OrderStatus(str, Enum):
    PENDING = "Pending"
    SHIPPED = "Shipped"
    CANCELLED = "Cancelled"

# Base Orders Schema
class Orders(BaseModel):
    stockist_id: str
    chemist_id: str
    order_date: datetime.datetime
    status: OrderStatus
    total_amount: int

# Database Schema
class OrdersDB(Orders):
    order_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# Schema for Creating a New Order
class OrdersCreate(BaseModel):
    stockist_id: str
    chemist_id: str
    order_date: datetime.datetime
    status: OrderStatus
    total_amount: int
