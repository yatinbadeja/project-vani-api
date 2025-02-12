from pydantic import BaseModel, Field, EmailStr
import datetime
from uuid import uuid4
from app.database.models.entity import phoneNumber,Name,Address

# Base Chemist Schema
class Chemist(BaseModel):
    user_id: str
    name: Name
    phone_number: phoneNumber
    shop_name: str
    address : Address # Assuming Address is stored as a string
    licence_number: str

# Database Schema (Includes ID and Timestamps)
class ChemistDB(Chemist):
    chemist_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# Schema for Creating a New Chemist (Excludes chemist_id and timestamps)
class ChemistCreate(BaseModel):
    name: Name
    phone_number: phoneNumber
    shop_name: str
    address: Address
    licence_number: str
