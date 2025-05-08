from typing import Optional, List, Dict, Any
from app.dbrm import Session

from app.crud import user as user_crud, customer, worker, admin
from app.schemas import User, UserUpdate, CustomerCreate, WorkerCreate, AdminCreate


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
    return user_crud.get_by_id(db, user_id=user_id)

def get_user_by_name(db: Session, user_name: str) -> Optional[User]:
    """Get a user by name"""
    return user_crud.get_by_name(db, user_name=user_name)

def update_user(db: Session, user_id: str, user_in: UserUpdate) -> Optional[User]:
    """Update a user's information (full update)"""
    user_obj = user_crud.get_by_id(db, user_id=user_id)
    if not user_obj:
        return None
    return user_crud.update(db, db_obj=user_obj, obj_in=user_in)


def partial_update_user(db: Session, user_id: str, obj_in: Dict[str, Any]) -> Optional[User]:
    """
    Partially update a user's information
    
    Only updates fields provided in the input dictionary
    """
    user_obj = user_crud.get_by_id(db, user_id=user_id)
    if not user_obj:
        return None
    
    # Convert dict to UserUpdate while preserving existing values
    user_data = user_obj.dict()
    for field in obj_in:
        if field in user_data:
            user_data[field] = obj_in[field]
    
    update_data = UserUpdate(**user_data)
    return user_crud.update(db, db_obj=user_obj, obj_in=update_data)


def delete_user(db: Session, user_id: str) -> bool:
    """
    Delete a user from the database
    
    Returns True if user was deleted, False if user was not found
    """
    user_obj = user_crud.get_by_id(db, user_id=user_id)
    if not user_obj:
        return False
    
    user_crud.remove(db, id=user_obj.id)
    return True


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    return user_crud.get_multi(db, skip=skip, limit=limit)
