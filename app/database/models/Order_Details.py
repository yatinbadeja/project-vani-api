from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict,List
# Base OrderDetails Schema

class Orders(BaseModel):
    product_id : str 
    quantity : int
    unit_price : float

class OrderDetails(BaseModel):
    order_id: str
    product_details: List[Orders]  # {Product_ID: {Quantity: x, Unit_Price: y}}

class OrderDetailsDB(OrderDetails):
    order_details_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

