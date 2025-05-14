from typing import Any, Dict, Optional, Union, List, Tuple
import time
import random
import string

from app.dbrm import Session, func

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User, Customer, Worker, Administrator
from app.schemas.user import UserCreate, UserUpdate, CustomerCreate, WorkerCreate, AdminCreate

def generate_unique_id(db: Session, user_type: str) -> str:
    prefix_map = {
        "customer": "C",
        "worker": "W", 
        "administrator": "A",
        "user": "U"
    }
    
    prefix = prefix_map.get(user_type.lower(), "U")
    timestamp = str(int(time.time()))[-6:]
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    
    user_id = f"{prefix}{timestamp}{random_chars}"
    
    while db.query(User).filter_by(user_id=user_id).first():
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        user_id = f"{prefix}{timestamp}{random_chars}"
    
    return user_id

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):    
    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter_by(user_id=user_id).first()
    
    def get_by_name(self, db: Session, user_name: str) -> Optional[User]:
        return db.query(User).filter_by(user_name=user_name).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        unique_id = generate_unique_id(db, obj_in.user_type)
        
        db_obj = User(
            user_id=unique_id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type=obj_in.user_type
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if update_data.get("user_pwd"):
            hashed_password = get_password_hash(update_data["user_pwd"])
            del update_data["user_pwd"]
            update_data["user_pwd"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, user_name: str, password: str) -> Optional[User]:
        user = self.get_by_name(db, user_name=user_name)
        if not user:
            return None
        if not verify_password(password, user.user_pwd):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return True

    def get_all_worker_types(self, db: Session) -> List[Tuple[int]]:
        return db.query(func.distinct(Worker.worker_type)).all()

    def count_workers_by_type(self, db: Session, worker_type: int, start_time: str, end_time: str) -> int:
        from app.dbrm import Condition
        return db.query(func.count(Worker.user_id)).where(
            Condition.eq(Worker.worker_type, worker_type),
            Condition.ge(Worker.created_at, start_time),
            Condition.le(Worker.created_at, end_time)
        ).scalar() or 0


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, UserUpdate]):
    def get_by_id(self, db: Session, customer_id: str) -> Optional[Customer]:
        return db.query(Customer).filter_by(user_id=customer_id).first()

    def create(self, db: Session, *, obj_in: CustomerCreate) -> Customer:
        unique_id = generate_unique_id(db, "customer")
        
        # First create a User object
        user_obj = User(
            user_id=unique_id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="customer"
        )
        db.add(user_obj)
        
        # Now create the Customer
        db_obj = Customer(
            user_id=unique_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDWorker(CRUDBase[Worker, WorkerCreate, UserUpdate]):
    def get_by_id(self, db: Session, worker_id: str) -> Optional[Worker]:
        return db.query(Worker).filter_by(user_id=worker_id).first()
    
    def get_by_name(self, db: Session, user_name: str) -> Optional[Worker]:
        return db.query(Worker).filter_by(user_name=user_name).first()

    def create(self, db: Session, *, obj_in: WorkerCreate) -> Worker:
        unique_id = generate_unique_id(db, "worker")
        
        # First create a User object
        user_obj = User(
            user_id=unique_id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="worker"
        )
        db.add(user_obj)
        
        # Now create the Worker
        db_obj = Worker(
            user_id=unique_id,
            worker_type=obj_in.worker_type
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_workers_by_type(self, db: Session, *, worker_type: int) -> List[Worker]:
        return db.query(Worker).filter_by(worker_type=worker_type).all()


class CRUDAdmin(CRUDBase[Administrator, AdminCreate, UserUpdate]):
    def get_by_id(self, db: Session, admin_id: str) -> Optional[Administrator]:
        return db.query(Administrator).filter_by(user_id=admin_id).first()

    def create(self, db: Session, *, obj_in: AdminCreate) -> Administrator:
        unique_id = generate_unique_id(db, "administrator")
        
        # First create a User object
        user_obj = User(
            user_id=unique_id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="administrator"
        )
        db.add(user_obj)
        
        # Now create the Administrator
        db_obj = Administrator(
            user_id=unique_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser(User)
customer = CRUDCustomer(Customer)
worker = CRUDWorker(Worker)
admin = CRUDAdmin(Administrator)
