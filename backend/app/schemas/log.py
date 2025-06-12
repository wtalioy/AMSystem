from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal


# Shared properties
class LogBase(BaseModel):
    consumption: str
    cost: Decimal
    duration: Decimal


# Properties to receive via API on creation
class LogCreate(LogBase):
    order_id: str


# Properties to receive via API on update
class LogUpdate(BaseModel):
    consumption: Optional[str] = None
    cost: Optional[Decimal] = None
    duration: Optional[Decimal] = None


# Properties shared by models stored in DB
class LogInDBBase(LogBase):
    log_time: datetime
    order_id: str
    worker_id: str

    class Config:
        from_attributes = True


# Properties to return via API
class Log(LogInDBBase):
    pass
