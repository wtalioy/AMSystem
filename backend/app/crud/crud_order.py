from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from decimal import Decimal

from app.dbrm import Session, func

from app.crud.base import CRUDBase
from app.models.order import ServiceOrder
from app.schemas.order import OrderCreate, OrderUpdate, OrderToAdmin


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
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        order_id = f"O{now.strftime('%y%m%d')}{random_suffix}"

        db_obj = ServiceOrder(
            order_id=order_id,
            description=obj_in.description,
            start_time=str(obj_in.start_time),
            end_time=None,
            car_id=obj_in.car_id,
            customer_id=customer_id,
            status=0,  # default to pending
            rating=None,
            worker_id=None,
            comment=None,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    

    
    def update_order_status(self, db: Session, order_id: str, new_status: int) -> ServiceOrder:
        """Update order status"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.status = new_status
            if new_status == 2:  # If completed
                db_obj.end_time = datetime.now()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def update_order_assignment(
        self, db: Session, order_id: str, worker_id: Optional[str], status: int
    ) -> ServiceOrder:
        """Update order worker assignment and status"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.worker_id = worker_id
            db_obj.status = status
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def get_completed_orders_count_by_worker_period(
        self, db: Session, worker_id: str, start_date: datetime, end_date: datetime
    ) -> int:
        """Get count of completed orders by worker in a date range"""
        from app.dbrm import Condition
        return db.query(func.count(ServiceOrder.order_id)).filter(
            Condition.eq(ServiceOrder.worker_id, worker_id),
            Condition.eq(ServiceOrder.status, 2),  # completed
            Condition.ge(ServiceOrder.end_time, start_date),
            Condition.le(ServiceOrder.end_time, end_date)
        ).scalar() or 0
    
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

    def set_expedite_flag(self, db: Session, order_id: str, expedite_time: datetime) -> ServiceOrder:
        """Set expedite flag and timestamp for an order"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.expedite_flag = True
            db_obj.expedite_time = expedite_time
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def update_order_total_cost(self, db: Session, order_id: str, total_cost: Decimal) -> ServiceOrder:
        """Update the total cost of an order"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.total_cost = total_cost
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


order = CRUDOrder(ServiceOrder)
