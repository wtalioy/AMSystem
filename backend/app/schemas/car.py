from typing import Optional
from pydantic import BaseModel


# Shared properties
class CarBase(BaseModel):
    car_type: int


# Properties to receive via API on creation
class CarCreate(CarBase):
    car_id: str
    customer_id: Optional[str] = None


# Properties to receive via API on update
class CarUpdate(CarBase):
    car_type: Optional[int] = None


# Properties shared by models stored in DB
class CarInDBBase(CarBase):
    car_id: str
    customer_id: str

    class Config:
        from_attributes = True  # Updated from orm_mode


# Properties to return via API
class Car(CarInDBBase):
    pass
