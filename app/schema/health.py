from typing import Union

from pydantic import BaseModel, ConfigDict, field_validator


class Health_Schema(BaseModel):
    success: bool
    status: int
    database_connected: bool
    app: str
    version: str
    ip_address: str
    uptime: Union[float, int]
    mode: str
    model_config = ConfigDict({"from_attributes": True})

    @field_validator("uptime")
    @classmethod
    def check_alphanumeric(cls, v: Union[float, int]) -> int:
        if isinstance(v, float):
            return int(v)
        return v
