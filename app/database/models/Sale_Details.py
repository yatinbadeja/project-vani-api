from pydantic import BaseModel, Field
import datetime
from uuid import uuid4

class SalesProduct(BaseModel):
    product_id: str
    quantity: int
    unit_price: float

class SaleDetails(SalesProduct):
    sale_id: str

class SaleDetailsDB(SaleDetails):
    sales_details_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))