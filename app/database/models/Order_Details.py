from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict
from typing import Dict

# Base OrderDetails Schema
class OrderDetails(BaseModel):
    order_id: str
    product_details: Dict[str, Dict[str, float]]  # {Product_ID: {Quantity: x, Unit_Price: y}}

# Database Schema
class OrderDetailsDB(OrderDetails):
    order_details_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# Schema for Creating New Order Details
class OrderDetailsCreate(BaseModel):
    order_id: str
    product_details: Dict[str, Dict[str, float]]
