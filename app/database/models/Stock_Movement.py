from pydantic import BaseModel, Field
from typing import Optional
import datetime
from uuid import uuid4
from app.schema.enums import StockMovementTypeEnum


class StockMovement(BaseModel):
    product_id: str
    quantity: int
    movement_type: Optional[StockMovementTypeEnum] = StockMovementTypeEnum.IN
    # reference_id: str
    chemist_id: str
    unit_price: float

class StockMovementDB(StockMovement):
    stock_movement_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
