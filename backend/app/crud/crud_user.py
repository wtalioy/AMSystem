from typing import Optional, List
import time
import random
import string

from app.dbrm import Session, func

from app.core.security import get_password_hash, verify_password
from app.models import User as UserModel, Customer as CustomerModel, Worker as WorkerModel, Administrator as AdministratorModel
from app.schemas import UserCreate, UserUpdate, CustomerCreate, WorkerCreate, AdminCreate, User
from app.core.enum import WorkerAvailabilityStatus

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
    
    while db.query(UserModel).filter_by(user_id=user_id).first():
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        user_id = f"{prefix}{timestamp}{random_chars}"
    
    return user_id

class CRUDUser:
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        objs = db.query(UserModel).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [User.model_validate(obj) for obj in objs]

    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        obj = db.query(UserModel).filter_by(user_id=user_id).first()
        if not obj:
            return None
        return User.model_validate(obj)
    
    def get_by_name(self, db: Session, user_name: str) -> Optional[User]:
        obj = db.query(UserModel).filter_by(user_name=user_name).first()
        if not obj:
            return None
        return User.model_validate(obj)

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        unique_id = generate_unique_id(db, obj_in.user_type)
        
        db_obj = UserModel(
            user_id=unique_id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type=obj_in.user_type
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return User.model_validate(db_obj)

    def update(
        self, db: Session, *, obj_old: User, obj_in: UserUpdate
    ) -> User:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            if hasattr(obj_old, field):
                setattr(obj_old, field, value)
        
        if hasattr(obj_in, "user_pwd"):
            db_obj = UserModel(
                user_id=obj_old.user_id,
                user_name=obj_old.user_name,
                user_pwd=get_password_hash(obj_in.user_pwd),
                user_type=obj_old.user_type
            )
        else:
            db_obj = UserModel(
                user_id=obj_old.user_id,
                user_name=obj_old.user_name,
                user_type=obj_old.user_type
            )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return User.model_validate(db_obj)
    
    def remove(self, db: Session, *, user_id: str) -> bool:
        obj = db.query(UserModel).filter_by(user_id=user_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def authenticate(self, db: Session, *, user_name: str, password: str) -> Optional[User]:
        user = db.query(UserModel).filter_by(user_name=user_name).first()
        if not user:
            return None
        if not verify_password(password, user.user_pwd):
            return None
        return User.model_validate(user)

    def is_active(self, user: UserModel) -> bool:
        return True


class CRUDCustomer:
    def get_by_id(self, db: Session, customer_id: str) -> Optional[User]:
        obj = db.query(CustomerModel).filter_by(user_id=customer_id).first()
        if not obj:
            return None
        return User.model_validate(obj)

    def create(self, db: Session, *, obj_in: CustomerCreate) -> User:
        unique_id = generate_unique_id(db, "customer")
        
        user_obj = UserModel(
            user_id=unique_id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="customer"
        )
        db.add(user_obj)
        
        customer_obj = CustomerModel(
            user_id=unique_id
        )
        db.add(customer_obj)
        db.commit()

        db.refresh(user_obj)
        return User.model_validate(user_obj)


class CRUDWorker:
    def get_by_id(self, db: Session, worker_id: str) -> Optional[User]:
        obj = db.query(WorkerModel).filter_by(user_id=worker_id).first()
        if not obj:
            return None
        return User.model_validate(obj)
    
    def get_by_name(self, db: Session, user_name: str) -> Optional[User]:
        obj = db.query(WorkerModel).filter_by(user_name=user_name).first()
        if not obj:
            return None
        return User.model_validate(obj)

    def create(self, db: Session, *, obj_in: WorkerCreate) -> User:
        unique_id = generate_unique_id(db, "worker")
        
        user_obj = UserModel(
            user_id=unique_id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="worker"
        )
        db.add(user_obj)
        
        worker_obj = WorkerModel(
            user_id=unique_id,
            worker_type=obj_in.worker_type
        )
        db.add(worker_obj)
        db.commit()

        db.refresh(user_obj)
        db.refresh(worker_obj)
        return User(
            user_id=user_obj.user_id,
            user_name=user_obj.user_name,
            user_type=user_obj.user_type,
            worker_type=worker_obj.worker_type
        )
        
    def get_workers_by_type(self, db: Session, *, worker_type: str) -> List[User]:
        objs = db.query(WorkerModel).filter_by(worker_type=worker_type).all()
        if not objs:
            return []
        return [User.model_validate(obj) for obj in objs]
    
    def get_available_workers(self, db: Session, worker_type: Optional[str] = None) -> List[User]:
        query = db.query(WorkerModel).filter_by(availability_status=WorkerAvailabilityStatus.AVAILABLE)
        if worker_type is not None:
            query = query.filter_by(worker_type=worker_type)
        objs = query.all()
        if not objs:
            return []
        return [User.model_validate(obj) for obj in objs]
    
    def get_all_worker_types(self, db: Session) -> List[str]:
        objs = db.query(func.distinct(WorkerModel.worker_type)).all()
        if not objs:
            return []
        return [obj[0] for obj in objs]

    def count_workers_by_type(self, db: Session, worker_type: str) -> int:
        return db.query(func.count(WorkerModel.user_id)).filter_by(worker_type=worker_type).scalar() or 0
    
    def update_availability(self, db: Session, worker_id: str, status: int) -> User:
        worker = self.get_by_id(db, worker_id)
        if worker:
            worker.availability_status = status
            db.add(worker)
            db.commit()
            db.refresh(worker)
        return User.model_validate(worker)
    
    def get_workers_by_status(self, db: Session, status: int) -> List[User]:
        """Get workers by availability status"""
        objs = db.query(WorkerModel).filter_by(availability_status=status).all()
        if not objs:
            return []
        return [User.model_validate(obj) for obj in objs]
    
    def get_all_active_workers(self, db: Session) -> List[User]:
        """Get all workers that are not deleted (active workers)"""
        objs = db.query(WorkerModel).filter(WorkerModel.deleted_at.is_(None)).all()
        if not objs:
            return []
        return [User.model_validate(obj) for obj in objs]


class CRUDAdmin:
    def get_by_id(self, db: Session, admin_id: str) -> Optional[User]:
        obj = db.query(AdministratorModel).filter_by(user_id=admin_id).first()
        if not obj:
            return None
        return User.model_validate(obj)

    def create(self, db: Session, *, obj_in: AdminCreate) -> User:
        unique_id = generate_unique_id(db, "administrator")
        
        user_obj = UserModel(
            user_id=unique_id,
            user_name=obj_in.user_name,
            user_pwd=get_password_hash(obj_in.user_pwd),
            user_type="administrator"
        )
        db.add(user_obj)
        
        admin_obj = AdministratorModel(
            user_id=unique_id
        )
        db.add(admin_obj)
        db.commit()

        db.refresh(user_obj)
        return User.model_validate(user_obj)


user = CRUDUser()
customer = CRUDCustomer()
worker = CRUDWorker()
admin = CRUDAdmin()
