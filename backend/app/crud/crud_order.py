from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from decimal import Decimal

from app.dbrm import Session, func

from app.models import ServiceOrder as ServiceOrderModel
from app.schemas import OrderCreate, Order
from app.core.enum import OrderStatus


class CRUDOrder:
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Order]:
        objs = db.query(ServiceOrderModel).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Order.model_validate(obj) for obj in objs]

    def get_by_order_id(self, db: Session, order_id: str) -> Optional[Order]:
        obj = db.query(ServiceOrderModel).filter_by(order_id=order_id).first()
        if not obj:
            return None
        return Order.model_validate(obj)
        
    def get_orders_by_customer(
        self, db: Session, customer_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[Order]:
        query = db.query(ServiceOrderModel).filter_by(customer_id=customer_id)
        if status is not None:
            query = query.filter_by(status=status)
        objs = query.offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Order.model_validate(obj) for obj in objs]
    
    def get_orders_by_worker(
        self, db: Session, worker_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[Order]:
        query = db.query(ServiceOrderModel).filter_by(worker_id=worker_id)
        if status is not None:
            query = query.filter_by(status=status)
        objs = query.offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Order.model_validate(obj) for obj in objs]
    
    def get_orders_by_worker_type(
        self, db: Session, worker_type: int, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[Order]:
        query = db.query(ServiceOrderModel).filter_by(worker_type=worker_type)
        if status is not None:
            query = query.filter_by(status=status)
        objs = query.offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Order.model_validate(obj) for obj in objs]

    def get_orders_by_car(
        self, db: Session, car_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[Order]:
        query = db.query(ServiceOrderModel).filter_by(car_id=car_id)
        if status is not None:
            query = query.filter_by(status=status)
        objs = query.offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Order.model_validate(obj) for obj in objs]
        
    def get_orders_by_status(
        self, db: Session, status: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        objs = db.query(ServiceOrderModel).filter_by(status=status).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Order.model_validate(obj) for obj in objs]
    
    def get_multi_with_details(
        self, db: Session, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[Union[OrderToAdmin, Order]]:
        """Get all orders with additional details for admin viewing"""
        query = db.query(ServiceOrderModel)
        if status is not None:
            query = query.filter_by(status=status)
        objs = query.offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Order.model_validate(obj) for obj in objs]
    
    def create_order_for_customer(
        self, db: Session, *, obj_in: OrderCreate, customer_id: str
    ) -> Order:
        # Generate unique order ID (in a real system, this would be more sophisticated)
        from datetime import datetime
        import random
        import string
        now = datetime.now()
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        order_id = f"O{now.strftime('%y%m%d')}{random_suffix}"

        db_obj = ServiceOrderModel(
            order_id=order_id,
            description=obj_in.description,
            start_time=str(obj_in.start_time),
            end_time=None,
            car_id=obj_in.car_id,
            customer_id=customer_id,
            status=OrderStatus.PENDING_ASSIGNMENT,  # default to pending
            rating=None,
            worker_id=None,
            comment=None,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Trigger automatic assignment
        try:
            from app.services.assignment_service import AutoAssignmentService
            AutoAssignmentService.trigger_assignment(db, db_obj.order_id)
        except Exception as e:
            # Log error but don't fail order creation
            print(f"Assignment failed for order {db_obj.order_id}: {e}")
        
        return Order.model_validate(db_obj)
    
    def update_order_status(self, db: Session, order_id: str, new_status: int) -> Order:
        """Update order status"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.status = new_status
            if new_status == OrderStatus.COMPLETED:  # If completed
                db_obj.end_time = datetime.now()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Order.model_validate(db_obj)
    
    def update_order_assignment(
        self, db: Session, order_id: str, worker_id: Optional[str], status: int
    ) -> Order:
        """Update order worker assignment and status"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.worker_id = worker_id
            db_obj.status = status
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Order.model_validate(db_obj)
    
    def get_completed_orders_count_by_worker_period(
        self, db: Session, worker_id: str, start_date: datetime, end_date: datetime
    ) -> int:
        """Get count of completed orders by worker in a date range"""
        from app.dbrm import Condition
        return db.query(func.count(ServiceOrderModel.order_id)).filter(
            Condition.eq(ServiceOrderModel.worker_id, worker_id),
            Condition.eq(ServiceOrderModel.status, OrderStatus.COMPLETED),  # completed
            Condition.ge(ServiceOrderModel.end_time, start_date),
            Condition.le(ServiceOrderModel.end_time, end_date)
        ).scalar() or 0
    
    def add_customer_feedback(
        self, db: Session, *, order_id: str, rating: int, comment: Optional[str] = None
    ) -> Order:
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.rating = rating
            if comment:
                db_obj.comment = comment
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Order.model_validate(db_obj)
    
    def get_total_orders_count(self, db: Session) -> int:
        return db.query(func.count(ServiceOrderModel.order_id)).scalar() or 0
    
    def count_orders_by_car_type(self, db: Session, car_type: int) -> int:
        from app.models.car import Car
        from app.dbrm import Condition
        return db.query(func.count(ServiceOrderModel.order_id)).join(
            Car, on=(Car.car_id, ServiceOrderModel.car_id)
        ).where(
            Condition.eq(Car.car_type, car_type)
        ).scalar() or 0
    
    def get_incomplete_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        from app.dbrm import Condition
        objs = db.query(ServiceOrderModel).filter(
            Condition.lt(ServiceOrderModel.status, OrderStatus.COMPLETED)
        ).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Order.model_validate(obj) for obj in objs]

    def set_expedite_flag(self, db: Session, order_id: str, expedite_time: datetime) -> Order:
        """Set expedite flag and timestamp for an order"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.expedite_flag = True
            db_obj.expedite_time = expedite_time
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Order.model_validate(db_obj)
    
    def update_order_total_cost(self, db: Session, order_id: str, total_cost: Decimal) -> Order:
        """Update the total cost of an order"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.total_cost = total_cost
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Order.model_validate(db_obj)

    def increment_assignment_attempts(self, db: Session, order_id: str) -> Order:
        """Increment assignment attempt counter and set deadline"""
        from datetime import datetime, timedelta
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.assignment_attempts += 1
            db_obj.last_assignment_at = datetime.now()
            db_obj.response_deadline = datetime.now() + timedelta(minutes=30)  # 30-minute deadline
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Order.model_validate(db_obj)
        
    def set_rejection_reason(self, db: Session, order_id: str, reason: str) -> Order:
        """Set rejection reason for order"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.rejection_reason = reason
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Order.model_validate(db_obj)
    
    def complete_order(self, db: Session, order_id: str) -> Order:
        """Mark an order as completed"""
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.status = OrderStatus.COMPLETED
            db_obj.end_time = datetime.now()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Order.model_validate(db_obj)


order = CRUDOrder()
