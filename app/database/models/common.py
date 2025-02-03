from pydantic import BaseModel, Field
from typing import List, Union,Optional
import datetime


class Username(BaseModel):
    first_name : str 
    middle_name : Optional[str]
    last_name : Optional[str]
    