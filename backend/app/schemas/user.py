from typing import Optional, List
from pydantic import BaseModel, Field, validator


# Shared properties
class UserBase(BaseModel):
    user_name: str


# Properties to receive via API on creation
class UserCreate(UserBase):
    user_pwd: str
    user_type: str


# Properties to receive via API on update
class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    user_pwd: Optional[str] = None


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: str
    user_type: str

    class Config:
        orm_mode = True


# Properties to return via API
class User(UserInDBBase):
    pass


# Properties stored in DB
class UserInDB(UserInDBBase):
    user_pwd: str


# Customer schemas
class CustomerBase(UserBase):
    pass


class CustomerCreate(UserCreate):
    user_type: str = "customer"


class CustomerUpdate(UserUpdate):
    pass


class CustomerInDBBase(UserInDBBase):
    class Config:
        orm_mode = True


class Customer(CustomerInDBBase):
    pass


# Worker schemas
class WorkerBase(UserBase):
    worker_type: int


class WorkerCreate(UserCreate):
    user_type: str = "worker"
    worker_type: int


class WorkerUpdate(UserUpdate):
    worker_type: Optional[int] = None


class WorkerInDBBase(UserInDBBase):
    worker_type: int

    class Config:
        orm_mode = True


class Worker(WorkerInDBBase):
    pass


# Administrator schemas
class AdminBase(UserBase):
    pass


class AdminCreate(UserCreate):
    user_type: str = "administrator"


class AdminUpdate(UserUpdate):
    pass


class AdminInDBBase(UserInDBBase):
    class Config:
        orm_mode = True


class Admin(AdminInDBBase):
    pass
