from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.crud.base import CRUDBase
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_by_order_id(self, db: Session, order_id: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_id == order_id).first()
        
    def get_orders_by_customer(
        self, db: Session, customer_id: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        return db.query(Order).filter(
            Order.customer_id == customer_id
        ).offset(skip).limit(limit).all()
        
    def get_orders_by_car(
        self, db: Session, car_id: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        return db.query(Order).filter(
            Order.car_id == car_id
        ).offset(skip).limit(limit).all()
        
    def get_orders_by_status(
        self, db: Session, status: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        return db.query(Order).filter(
            Order.status == status
        ).offset(skip).limit(limit).all()
    
    def create_order_for_customer(
        self, db: Session, *, obj_in: OrderCreate, customer_id: str
    ) -> Order:
        # Generate unique order ID (in a real system, this would be more sophisticated)
        from datetime import datetime
        import random
        import string
        now = datetime.now()
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        order_id = f"O{now.strftime('%y%m%d')}{random_suffix}"
        
        db_obj = Order(
            order_id=order_id,
            description=obj_in.description,
            car_id=obj_in.car_id,
            customer_id=customer_id,
            status=0  # default to pending
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_order_status(
        self, db: Session, *, order_id: str, new_status: int
    ) -> Order:
        db_obj = self.get_by_order_id(db, order_id=order_id)
        if db_obj:
            db_obj.status = new_status
            if new_status == 2:  # If completed
                db_obj.end_time = datetime.now()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
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
        return db_obj


order = CRUDOrder(Order)
