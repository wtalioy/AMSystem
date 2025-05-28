from typing import Optional, List, Dict, Any, Union
from app.dbrm import Session

from app.crud import user as user_crud, customer, worker, admin
from app.schemas import User, UserUpdate, CustomerCreate, WorkerCreate, AdminCreate, Customer, Worker, Admin


def _convert_user_to_typed_object(db: Session, user_obj) -> Union[Customer, Worker, Admin, User]:
    """Convert a database user object to the appropriate typed schema object"""
    if not user_obj:
        return None
    
    base_data = {
        "user_id": user_obj.user_id,
        "user_name": user_obj.user_name,
        "user_type": user_obj.user_type
    }
    
    if user_obj.user_type == "customer":
        return Customer(**base_data)
    elif user_obj.user_type == "worker":
        worker_obj = worker.get_by_id(db, worker_id=user_obj.user_id)
        return Worker(**base_data, worker_type=worker_obj.worker_type if worker_obj else 0)
    elif user_obj.user_type == "administrator":
        return Admin(**base_data)
    else:
        return User(**base_data)


def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
    """Create a new customer user"""
    user_obj = customer.create(db, obj_in=customer_in)
    return _convert_user_to_typed_object(db, user_obj)


def create_worker(db: Session, worker_in: WorkerCreate) -> Worker:
    """Create a new worker user"""
    user_obj = worker.create(db, obj_in=worker_in)
    return _convert_user_to_typed_object(db, user_obj)


def create_admin(db: Session, admin_in: AdminCreate) -> Admin:
    """Create a new administrator user"""
    user_obj = admin.create(db, obj_in=admin_in)
    return _convert_user_to_typed_object(db, user_obj)


def get_user_by_id(db: Session, user_id: str, typed: bool = False) -> Optional[Union[User, Customer, Worker, Admin]]:
    """Get a user by ID, optionally returning the typed object"""
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        return None
    
    if typed:
        return _convert_user_to_typed_object(db, user)
    else:
        return User.model_validate(user)


def get_user_by_name(db: Session, user_name: str) -> Optional[User]:
    """Get a user by name"""
    user = user_crud.get_by_name(db, user_name=user_name)
    if user is not None:
        return User.model_validate(user)
    return None


def update_user(db: Session, user_id: str, user_in: UserUpdate) -> Optional[User]:
    """Update a user's information (full update)"""
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        return None
    
    return User.model_validate(user_crud.update(db, db_obj=user, obj_in=user_in))


def partial_update_user(db: Session, user_id: str, obj_in: Dict[str, Any]) -> Optional[User]:
    """
    Partially update user information
    
    Only updates the fields that are provided in the input dictionary
    """
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        return None
    
    # Convert dict to UserUpdate while preserving existing values
    user_data = user.dict()
    for field in obj_in:
        if field in user_data:
            user_data[field] = obj_in[field]
    
    update_data = UserUpdate(**user_data)
    return User.model_validate(user_crud.update(db, db_obj=user, obj_in=update_data))


def delete_user(db: Session, user_id: str) -> bool:
    """
    Delete a user from the database
    
    Returns True if user was deleted, False if user was not found
    """
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        return False
    
    user_crud.remove(db, id=user.id)
    return True


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    return [User.model_validate(u) for u in users]


def get_customer_by_id(db: Session, user_id: str) -> Optional[Customer]:
    """Get a customer by ID, returns None if user is not a customer"""
    user = get_user_by_id(db, user_id=user_id, typed=True)
    return user if isinstance(user, Customer) else None


def get_worker_by_id(db: Session, user_id: str) -> Optional[Worker]:
    """Get a worker by ID, returns None if user is not a worker"""
    user = get_user_by_id(db, user_id=user_id, typed=True)
    return user if isinstance(user, Worker) else None


def get_admin_by_id(db: Session, user_id: str) -> Optional[Admin]:
    """Get an admin by ID, returns None if user is not an admin"""
    user = get_user_by_id(db, user_id=user_id, typed=True)
    return user if isinstance(user, Admin) else None


def verify_user_type(user: User, expected_type: str) -> bool:
    """Verify if a user has the expected type"""
    return user.user_type == expected_type


def get_typed_user_by_id(db: Session, user_id: str, expected_type: str) -> Optional[Union[Customer, Worker, Admin]]:
    """Get a typed user by ID, ensuring they have the expected type"""
    user = get_user_by_id(db, user_id=user_id, typed=True)
    if not user or not verify_user_type(user, expected_type):
        return None
    return user
