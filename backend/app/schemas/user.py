from typing import Optional
from pydantic import BaseModel


# For creating new users
class UserCreate(BaseModel):
    user_name: str
    user_pwd: str
    user_type: str
    worker_type: Optional[str] = None


# For user login
class UserLogin(BaseModel):
    user_name: str
    user_pwd: str


# For updating users
class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    user_pwd: Optional[str] = None
    worker_type: Optional[str] = None


# Main user schema
class User(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    user_type: Optional[str] = None
    worker_type: Optional[str] = None
    availability_status: Optional[int] = None

    class Config:
        from_attributes = True


# Specialized user types
class Customer(BaseModel):
    user_id: str
    user_type: str = "customer"


class Worker(BaseModel):
    user_id: str
    user_type: str = "worker"
    worker_type: str
    availability_status: int


class Admin(BaseModel):
    user_id: str
    user_type: str = "administrator"


# For backward compatibility with existing CRUD operations
CustomerCreate = UserCreate
WorkerCreate = UserCreate  
AdminCreate = UserCreate
