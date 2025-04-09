from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum

class ProductStock(BaseModel):
    product_id: str
    available_quantity: int
    chemist_id: str

class ProductStockDB(ProductStock):
    product_stock_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
