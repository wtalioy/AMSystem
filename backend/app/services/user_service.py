from typing import Optional, List
from app.dbrm import Session

from app.crud.crud_user import user, customer, worker, admin
from app.schemas.user import UserCreate, UserUpdate, CustomerCreate, WorkerCreate, AdminCreate
from app.models.user import User


def create_customer(db: Session, customer_in: CustomerCreate) -> User:
    """Create a new customer user"""
    return customer.create(db, obj_in=customer_in)


def create_worker(db: Session, worker_in: WorkerCreate) -> User:
    """Create a new worker user"""
    return worker.create(db, obj_in=worker_in)


def create_admin(db: Session, admin_in: AdminCreate) -> User:
    """Create a new administrator user"""
    return admin.create(db, obj_in=admin_in)


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get a user by ID"""
    return user.get_by_id(db, user_id=user_id)


def update_user(db: Session, user_id: str, user_in: UserUpdate) -> Optional[User]:
    """Update a user's information"""
    user = user.get_by_id(db, user_id=user_id)
    if not user:
        return None
    return user.update(db, db_obj=user, obj_in=user_in)


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users"""
    return user.get_multi(db, skip=skip, limit=limit)
