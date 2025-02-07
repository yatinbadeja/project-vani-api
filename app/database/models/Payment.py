from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum

# Enum for Payment Mode
class PaymentMode(str, Enum):
    CASH = "Cash"
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    ONLINE = "Online"

# Base Payment Schema
class Payment(BaseModel):
    invoice_id: str
    amount: float
    payment_mode: PaymentMode

# Database Schema (Includes ID and Timestamps)
class PaymentDB(Payment):
    payment_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# Schema for Creating a New Payment (Excludes ID and Timestamps)
class PaymentCreate(BaseModel):
    invoice_id: str
    amount: float
    payment_mode: PaymentMode
