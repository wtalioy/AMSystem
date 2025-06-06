from typing import Optional
from pydantic import BaseModel


# Base user schema
class UserBase(BaseModel):
    user_name: str
    user_type: str


# For creating new users
class UserCreate(UserBase):
    user_pwd: str
    worker_type: Optional[int] = None  # Only used for workers


# For user login
class UserLogin(BaseModel):
    user_name: str
    user_pwd: str


# For updating users
class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    user_pwd: Optional[str] = None
    worker_type: Optional[int] = None


# Main user schema (returned by API)
class User(UserBase):
    user_id: str
    worker_type: Optional[int] = None

    class Config:
        from_attributes = True


# Specialized user types (simplified)
class Customer(User):
    user_type: str = "customer"


class Worker(User):
    user_type: str = "worker"
    worker_type: int  # Required for workers


class Admin(User):
    user_type: str = "administrator"


# For backward compatibility with existing CRUD operations
CustomerCreate = UserCreate
WorkerCreate = UserCreate  
AdminCreate = UserCreate
