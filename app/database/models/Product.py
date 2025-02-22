from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum

# Enum for Product State
class ProductState(str, Enum):
    SOLID = "Solid"
    LIQUID = "Liquid"
    GAS = "Gas"

# Base Product Schema
class Product(BaseModel):
    product_name: str
    category: str
    state: ProductState
    measure_of_unit: str
    no_of_tablets_per_pack: int | None  # Nullable field
    price: float
    storage_requirement: str  # Example: Room Temp / Cold Chain
    description: str
    expiry_date: datetime.datetime


# Database Schema
class ProductDB(Product):
    product_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# Schema for Creating a New Product
class ProductCreate(BaseModel):
    product_name: str
    category: str
    state: ProductState
    measure_of_unit: str
    no_of_tablets_per_pack: int | None
    price: float
    storage_requirement: str
    description: str
    expiry_date: datetime.datetime
