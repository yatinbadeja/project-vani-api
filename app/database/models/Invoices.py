from pydantic import BaseModel, Field
import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict
# Enum for Payment Status
class PaymentStatus(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"

# Base Invoices Schema
class Invoices(BaseModel):
    order_id: str
    issue_date: datetime.datetime
    due_date: datetime.datetime
    total_amount: float
    payment_status: PaymentStatus

# Database Schema
class InvoicesDB(Invoices):
    invoice_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# Schema for Creating a New Invoice
class InvoicesCreate(BaseModel):
    order_id: str
    issue_date: datetime.datetime
    due_date: datetime.datetime
    total_amount: float
    payment_status: PaymentStatus
