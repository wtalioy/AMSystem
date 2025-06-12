from typing import Optional
from pydantic import BaseModel


# Shared properties
class CarBase(BaseModel):
    car_type: str


# Properties to receive via API on creation
class CarCreate(CarBase):
    car_id: str


# Properties to receive via API on update
class CarUpdate(CarBase):
    car_type: Optional[str] = None


# Properties shared by models stored in DB
class CarInDBBase(CarBase):
    car_id: str
    customer_id: str

    class Config:
        from_attributes = True  # Updated from from_attributes


# Properties to return via API
class Car(CarInDBBase):
    pass


class CarType(BaseModel):
    car_type: str
