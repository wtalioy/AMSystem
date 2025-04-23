from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User, Customer, Worker, Administrator
from app.schemas.user import UserCreate, UserUpdate, CustomerCreate, WorkerCreate, AdminCreate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            id=obj_in.id,
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
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("user_pwd"):
            hashed_password = get_password_hash(update_data["user_pwd"])
            del update_data["user_pwd"]
            update_data["user_pwd"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, user_id: str, password: str) -> Optional[User]:
        user = self.get_by_id(db, user_id=user_id)
        if not user:
            return None
        if not verify_password(password, user.user_pwd):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return True


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, UserUpdate]):
    def get_by_id(self, db: Session, customer_id: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.user_id == customer_id).first()

    def create(self, db: Session, *, obj_in: CustomerCreate) -> Customer:
        # First create a User object
        user_obj = User(
            id=obj_in.id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="customer"
        )
        db.add(user_obj)
        db.commit()
        
        # Now create the Customer
        db_obj = Customer(
            user_id=obj_in.id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDWorker(CRUDBase[Worker, WorkerCreate, UserUpdate]):
    def get_by_id(self, db: Session, worker_id: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.user_id == worker_id).first()

    def create(self, db: Session, *, obj_in: WorkerCreate) -> Worker:
        # First create a User object
        user_obj = User(
            id=obj_in.id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="worker"
        )
        db.add(user_obj)
        db.commit()
        
        # Now create the Worker
        db_obj = Worker(
            user_id=obj_in.id,
            worker_type=obj_in.worker_type
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_workers_by_type(self, db: Session, *, worker_type: int) -> List[Worker]:
        return db.query(Worker).filter(Worker.worker_type == worker_type).all()


class CRUDAdmin(CRUDBase[Administrator, AdminCreate, UserUpdate]):
    def get_by_id(self, db: Session, admin_id: str) -> Optional[Administrator]:
        return db.query(Administrator).filter(Administrator.user_id == admin_id).first()

    def create(self, db: Session, *, obj_in: AdminCreate) -> Administrator:
        # First create a User object
        user_obj = User(
            id=obj_in.id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="administrator"
        )
        db.add(user_obj)
        db.commit()
        
        # Now create the Administrator
        db_obj = Administrator(
            user_id=obj_in.id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser(User)
customer = CRUDCustomer(Customer)
worker = CRUDWorker(Worker)
admin = CRUDAdmin(Administrator)
