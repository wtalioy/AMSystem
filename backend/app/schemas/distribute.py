from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal


# Shared properties
class DistributeBase(BaseModel):
    amount: Decimal
    worker_id: str


# Properties to receive via API on creation
class DistributeCreate(DistributeBase):
    pass


# Properties to receive via API on update
class DistributeUpdate(BaseModel):
    amount: Optional[Decimal] = None


# Properties shared by models stored in DB
class DistributeInDBBase(DistributeBase):
    distribute_id: int
    distribute_time: datetime

    class Config:
        from_attributes = True


# Properties to return via API
class Distribute(DistributeInDBBase):
    pass
