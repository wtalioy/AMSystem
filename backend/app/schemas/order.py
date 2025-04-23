from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, validator
from decimal import Decimal


# Shared properties
class OrderBase(BaseModel):
    description: str
    car_id: str


# Properties to receive via API on creation
class OrderCreate(OrderBase):
    pass


# Properties to receive via API on update
class OrderUpdate(BaseModel):
    description: Optional[str] = None
    rating: Optional[int] = None
    comment: Optional[str] = None
    status: Optional[int] = None
    end_time: Optional[datetime] = None
    
    @validator('rating')
    def rating_must_be_valid(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v


# Properties shared by models stored in DB
class OrderInDBBase(OrderBase):
    order_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    rating: Optional[int] = None
    comment: Optional[str] = None
    status: int  # 0: pending, 1: in progress, 2: completed
    customer_id: str

    class Config:
        orm_mode = True


# Properties to return via API
class Order(OrderInDBBase):
    pass


# Properties with procedures included
class OrderWithProcedures(Order):
    procedures: List["Procedure"] = []


# Properties with logs included
class OrderWithLogs(Order):
    logs: List["Log"] = []
