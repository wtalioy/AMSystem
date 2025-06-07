from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.dbrm import Session

from app.crud import order, user, car
from app.schemas import OrderCreate, OrderUpdate, Order
from app.core.audit_decorators import audit
from app.core.enum import OrderStatus


class OrderService:
    """Service for order operations"""

    @staticmethod
    @audit("Order", "CREATE")
    def create_order(db: Session, obj_in: OrderCreate, customer_id: str, audit_context=None) -> Order:
        """Create a new service order"""
        return order.create_order_for_customer(db=db, obj_in=obj_in, customer_id=customer_id)


    @staticmethod
    def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
        """Get a specific order by ID"""
        order_obj = order.get_by_order_id(db, order_id=order_id)
        return order_obj


    @staticmethod
    def get_customer_orders(db: Session, customer_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders for a customer with pagination"""
        orders = order.get_orders_by_customer(db, customer_id=customer_id, skip=skip, limit=limit)
        return orders


    @staticmethod
    def get_worker_orders(db: Session, worker_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders assigned to a worker with pagination"""
        orders = order.get_orders_by_worker(db, worker_id=worker_id, skip=skip, limit=limit)
        return orders


    @staticmethod
    @audit("Order", "DELETE")
    def delete_order(db: Session, order_id: str, audit_context=None) -> bool:
        """
        Delete an order from the database
        
        Returns True if order was deleted, False if order was not found
        """
        order_obj = order.get_by_order_id(db, order_id=order_id)
        if not order_obj:
            return False
        
        order.remove(db, id=order_obj.id)
        return True


    @staticmethod
    def get_pending_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all pending orders (admin function)"""
        orders = order.get_by_status(db, status=OrderStatus.PENDING_ASSIGNMENT, skip=skip, limit=limit)
        return orders


    @staticmethod
    def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders (admin function)"""
        orders = order.get_multi(db, skip=skip, limit=limit)
        return orders


    @staticmethod
    @audit("Order", "UPDATE")
    def complete_order(db: Session, order_id: str, audit_context=None) -> Order:
        """Mark an order as completed"""
        return order.complete_order(db, order_id)


    @staticmethod
    def get_order_details_with_car(db: Session, order_id: str) -> Optional[Dict]:
        """
        Get order details along with car information
        
        Returns a dictionary containing order and car data
        """
        order_obj = order.get_by_order_id(db, order_id=order_id)
        if not order_obj:
            return None
        
        # Get car information
        car_obj = car.get_by_car_id(db, car_id=order_obj.car_id)
        car_data = car_obj.__dict__ if car_obj else None
        
        # Get customer information
        customer_obj = user.get_by_id(db, user_id=order_obj.customer_id)
        customer_data = customer_obj.__dict__ if customer_obj else None
        
        # Get worker information
        worker_obj = user.get_by_id(db, user_id=order_obj.worker_id) if order_obj.worker_id else None
        worker_data = worker_obj.__dict__ if worker_obj else None
        
        return {
            "order": order_obj.__dict__,
            "car": car_data,
            "customer": customer_data,
            "worker": worker_data
        }
