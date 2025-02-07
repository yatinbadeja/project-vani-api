from pydantic import BaseModel, Field
import datetime
from uuid import uuid4

# Base Inventory Schema
class Inventory(BaseModel):
    chemist_id: str
    product_id: str
    quantity: int
    last_restock_date: datetime.date

# Database Schema (Includes ID and Timestamps)
class InventoryDB(Inventory):
    inventory_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# Schema for Creating New Inventory (Excludes inventory_id and timestamps)
class InventoryCreate(BaseModel):
    chemist_id: str
    product_id: str
    quantity: int
    last_restock_date: datetime.date
