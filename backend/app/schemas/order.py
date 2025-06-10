from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator


# Shared properties
class OrderBase(BaseModel):
    description: str
    car_id: str


# Properties to receive via API on creation
class OrderCreate(OrderBase):
    start_time: datetime


# Properties to receive via API on update
class OrderUpdate(BaseModel):
    description: Optional[str] = None
    rating: Optional[int] = None
    comment: Optional[str] = None
    status: Optional[int] = None
    end_time: Optional[datetime] = None
    
    @field_validator('rating')
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
    status: int
    customer_id: str
    worker_id: Optional[str] = None
    total_cost: Optional[Decimal] = None
    expedite_flag: bool = False
    assignment_attempts: int = 0
    last_assignment_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Order(OrderInDBBase):
    pass


# Properties to return to workers
class OrderToWorker(OrderBase):
    order_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    rating: Optional[int] = None
    comment: Optional[str] = None
    status: int
    expedite_flag: bool = False


# Properties to return to customers
class OrderToCustomer(OrderToWorker):
    pass


# Properties sto return to admins
class OrderToAdmin(OrderInDBBase):
    pass


class OrderPending(OrderBase):
    order_id: str
    start_time: datetime
    car_type: Optional[str] = None

    class Config:
        from_attributes = True