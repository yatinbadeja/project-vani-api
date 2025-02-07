from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict
# Base Stockist Schema
class Stockist(BaseModel):
    user_id: str
    name: str
    company_name: str
    address: str
    email: str
    phone_number: int

# Database Schema
class StockistDB(Stockist):
    stockist_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# Schema for Creating a New Stockist
class StockistCreate(BaseModel):
    user_id: str
    name: str
    company_name: str
    address: str
    email: str
    phone_number: int
