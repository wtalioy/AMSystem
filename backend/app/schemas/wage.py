from pydantic import BaseModel
from typing import Optional


# Shared properties
class WageBase(BaseModel):
    wage_per_hour: int


# Properties to receive via API on creation
class WageCreate(WageBase):
    worker_type: str


# Properties to receive via API on update
class WageUpdate(WageBase):
    worker_type: str


# Properties shared by models stored in DB
class WageInDBBase(WageBase):
    worker_type: str

    class Config:
        from_attributes = True


# Properties to return via API
class Wage(WageInDBBase):
    pass
