from pydantic import BaseModel
from typing import Union, Optional,Dict
import datetime

class Name(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None


class phoneNumber(BaseModel):
    country_code: str = "+91"
    phone_number: str


class Address(BaseModel):
    street_address: Optional[str] = None
    street_address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None



