from typing import Optional, List
from app.dbrm import Session

from app.crud import user as user_crud, customer, worker, admin, wage
from app.schemas import User, UserUpdate, UserCreate
from app.core.audit_decorators import audit

class UserService:
    """Service for user operations with audit trail"""

    @staticmethod
    @audit("User", "CREATE")
    def create_user(db: Session, obj_in: UserCreate, audit_context=None) -> User:
        """Create a new user"""
        if obj_in.user_type == "customer":
            user_obj = customer.create(db, obj_in=obj_in)
        elif obj_in.user_type == "worker":
            from app.services import wage_service
            wage_obj = wage_service.get_wage_by_worker_type(db, obj_in.worker_type)
            if not wage_obj:
                raise ValueError(f"Unsupported worker type: {obj_in.worker_type}")
            user_obj = worker.create(db, obj_in=obj_in)
        elif obj_in.user_type == "administrator":
            user_obj = admin.create(db, obj_in=obj_in)
        else:
            raise ValueError(f"Invalid user type: {obj_in.user_type}")
        return user_obj
            

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        user = user_crud.get_by_id(db, user_id=user_id)
        if user:
            return user
        return None

    @staticmethod
    def get_user_by_name(db: Session, user_name: str) -> Optional[User]:
        """Get a user by name"""
        user = user_crud.get_by_name(db, user_name=user_name)
        if user:
            return user
        return None

    @staticmethod
    @audit("User", "UPDATE")
    def update_user(db: Session, user_id: str, obj_in: UserUpdate, audit_context=None) -> Optional[User]:
        """Update user information"""
        user = user_crud.get_by_id(db, user_id=user_id)
        if not user:
            return None
        
        # CRUD layer handles password hashing, so pass data directly
        updated_user = user_crud.update(db, obj_old=user, obj_in=obj_in)
        return updated_user

    @staticmethod
    @audit("User", "DELETE")
    def delete_user(db: Session, user_id: str, audit_context=None) -> bool:
        """Delete a user"""
        user = user_crud.get_by_id(db, user_id=user_id)
        if not user:
            return False
        
        user_crud.remove(db, user_id=user.user_id)
        return True

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination (admin function)"""
        users = user_crud.get_multi(db, skip=skip, limit=limit)
        return users

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: str) -> Optional[User]:
        """Get a customer by ID"""
        customer_obj = customer.get_by_id(db, customer_id=customer_id)
        if customer_obj:
            return customer_obj
        return None

    @staticmethod
    def get_worker_by_id(db: Session, worker_id: str) -> Optional[User]:
        """Get a worker by ID"""
        worker_obj = worker.get_by_id(db, worker_id=worker_id)
        if worker_obj:
            return worker_obj
        return None

    @staticmethod
    def get_admin_by_id(db: Session, admin_id: str) -> Optional[User]:
        """Get an administrator by ID"""
        admin_obj = admin.get_by_id(db, admin_id=admin_id)
        if admin_obj:
            return admin_obj
        return None

    @staticmethod
    def verify_user_type(user: User, expected_type: str) -> bool:
        """Verify if a user has the expected type"""
        return user.user_type == expected_type

    @staticmethod
    def get_typed_user_by_id(db: Session, user_id: str, expected_type: str) -> Optional[User]:
        """Get a typed user by ID, ensuring they have the expected type"""
        user = UserService.get_user_by_id(db, user_id=user_id)
        if not user or not UserService.verify_user_type(user, expected_type):
            return None
        
        return user
    
    @staticmethod
    def get_valid_worker_types(db: Session) -> List[str]:
        return wage.get_all_types(db)