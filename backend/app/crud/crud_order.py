from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from app.dbrm import Session, func

from app.crud.base import CRUDBase
from app.models.order import ServiceOrder
from app.schemas.order import OrderCreate, OrderUpdate, OrderToAdmin, OrderToCustomer


class CRUDOrder(CRUDBase[ServiceOrder, OrderCreate, OrderUpdate]):
    def get_by_order_id(self, db: Session, order_id: str) -> Optional[ServiceOrder]:
        return db.query(ServiceOrder).filter_by(order_id=order_id).first()
        
    def get_orders_by_customer(
        self, db: Session, customer_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[ServiceOrder]:
        query = db.query(ServiceOrder).filter_by(customer_id=customer_id)
        if status is not None:
            query = query.filter_by(status=status)
        return query.offset(skip).limit(limit).all()
    
    def get_orders_by_worker(
        self, db: Session, worker_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[ServiceOrder]:
        query = db.query(ServiceOrder).filter_by(worker_id=worker_id)
        if status is not None:
            query = query.filter_by(status=status)
        return query.offset(skip).limit(limit).all()
    
    def get_orders_by_worker_type(
        self, db: Session, worker_type: int, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[ServiceOrder]:
        query = db.query(ServiceOrder).filter_by(worker_type=worker_type)
        if status is not None:
            query = query.filter_by(status=status)
        return query.offset(skip).limit(limit).all()

    def get_orders_by_car(
        self, db: Session, car_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[ServiceOrder]:
        query = db.query(ServiceOrder).filter_by(car_id=car_id)
        if status is not None:
            query = query.filter_by(status=status)
        return query.offset(skip).limit(limit).all()
        
    def get_orders_by_status(
        self, db: Session, status: int, skip: int = 0, limit: int = 100
    ) -> List[ServiceOrder]:
        return db.query(ServiceOrder).filter_by(status=status).offset(skip).limit(limit).all()
    
    def get_multi_with_details(
        self, db: Session, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[Union[OrderToAdmin, ServiceOrder]]:
        """Get all orders with additional details for admin viewing"""
        query = db.query(ServiceOrder)
        if status is not None:
            query = query.filter_by(status=status)
        return query.offset(skip).limit(limit).all()
    
    def create_order_for_customer(
        self, db: Session, *, obj_in: OrderCreate, customer_id: str
    ) -> ServiceOrder:
        # Generate unique order ID (in a real system, this would be more sophisticated)
        from datetime import datetime
        import random
        import string
        now = datetime.now()
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        order_id = f"O{now.strftime('%y%m%d')}{random_suffix}"

        db_obj = ServiceOrder(
            order_id=order_id,
            description=obj_in.description,
            car_id=obj_in.car_id,
            customer_id=customer_id,
            status=0,  # default to pending
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_status(
        self, db: Session, *, order_id: str, new_status: int, worker_id: Optional[str] = None
    ) -> ServiceOrder:
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.status = new_status
            if new_status == 2:  # If completed
                db_obj.end_time = datetime.now()
            if worker_id:
                db_obj.worker_id = worker_id
                db_obj.status = 1  # In progress
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def add_customer_feedback(
        self, db: Session, *, order_id: str, rating: int, comment: Optional[str] = None
    ) -> ServiceOrder:
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.rating = rating
            if comment:
                db_obj.comment = comment
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def get_total_orders_count(self, db: Session) -> int:
        return db.query(func.count(ServiceOrder.order_id)).scalar() or 0
    
    def count_orders_by_car_type(self, db: Session, car_type: int) -> int:
        from app.models.car import Car
        from app.dbrm import Condition
        return db.query(func.count(ServiceOrder.order_id)).join(
            Car, on=(Car.car_id, ServiceOrder.car_id)
        ).where(
            Condition.eq(Car.car_type, car_type)
        ).scalar() or 0

    def get_pending_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[ServiceOrder]:
        return db.query(ServiceOrder).filter_by(status=0).offset(skip).limit(limit).all()

    def get_in_progress_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[ServiceOrder]:
        return db.query(ServiceOrder).filter_by(status=1).offset(skip).limit(limit).all()

    def get_completed_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[ServiceOrder]:
        return db.query(ServiceOrder).filter_by(status=2).offset(skip).limit(limit).all()
    
    def get_incomplete_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[ServiceOrder]:
        from app.dbrm import Condition
        return db.query(ServiceOrder).filter(
            Condition.lt(ServiceOrder.status, 2)
        ).offset(skip).limit(limit).all()


order = CRUDOrder(ServiceOrder)
