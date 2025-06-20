from typing import Optional, List, Dict
from app.dbrm import Session

from app.crud import order, user, car
from app.schemas import OrderCreate, Order
from app.core.audit_decorators import audit
from app.core.enum import OrderStatus
from app.background.assignment_processor import trigger_assignment


class OrderService:
    """Service for order operations"""

    @staticmethod
    @audit("Order", "CREATE")
    def create_order(db: Session, obj_in: OrderCreate, customer_id: str, audit_context=None) -> Order:
        """Create a new service order"""
        order_obj = order.create_order_for_customer(db=db, obj_in=obj_in, customer_id=customer_id)
        trigger_assignment(db, order_obj.order_id)
        return order_obj


    @staticmethod
    def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
        """Get a specific order by ID"""
        order_obj = order.get_by_order_id(db, order_id=order_id)
        return order_obj


    @staticmethod
    def get_customer_orders(db: Session, customer_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None) -> List[Order]:
        """Get all orders for a customer with pagination"""
        orders = order.get_orders_by_customer(db, customer_id=customer_id, skip=skip, limit=limit, status=status)
        return orders


    @staticmethod
    def get_worker_orders(db: Session, worker_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None) -> List[Order]:
        """Get all orders assigned to a worker with pagination"""
        orders = order.get_orders_by_worker(db, worker_id=worker_id, skip=skip, limit=limit, status=status)
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
        
        order.remove(db, order_id=order_id)
        return True


    @staticmethod
    def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders (admin function)"""
        orders = order.get_multi(db, skip=skip, limit=limit)
        return orders


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


    @staticmethod
    @audit("Order", "UPDATE")
    def add_customer_feedback(
        db: Session, 
        order_id: str, 
        rating: int, 
        comment: Optional[str] = None, 
        audit_context=None
    ) -> Order:
        """Add customer feedback (rating and comment) to a completed order"""
        # Validate rating
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        return order.add_customer_feedback(db, order_id=order_id, rating=rating, comment=comment)


    @staticmethod
    @audit("Order", "UPDATE")
    def expedite_order(db: Session, order_id: str, user_id: str, audit_context=None) -> Order:
        """
        Expedite an order - marks it for priority handling
        
        This sets the expedite flag and timestamp, which can be used by:
        - Assignment algorithms to prioritize expedited orders
        - Workers to see which orders need urgent attention
        - Analytics to track expedited order performance
        """
        order_obj = order.get_by_order_id(db, order_id=order_id)
        if not order_obj:
            raise ValueError("Order not found")
        
        if order_obj.customer_id != user_id:
            raise ValueError("Not authorized to expedite this order")
        
        # Check if order can be expedited
        if order_obj.status >= OrderStatus.COMPLETED:
            raise ValueError("Cannot expedite completed or cancelled orders")
        
        # Check if already expedited
        if order_obj.expedite_flag:
            raise ValueError("Order is already expedited")
        
        # Set expedite flag
        updated_order = order.set_expedite_flag(db, order_id=order_id)
        
        # Optionally trigger re-assignment for better worker matching
        # This could be enhanced to notify available workers immediately
        try:
            if order_obj.status == OrderStatus.PENDING_ASSIGNMENT:
                trigger_assignment(db, order_id=order_id)
        except Exception as e:
            # Log error but don't fail the expedite request
            print(f"Priority assignment failed for expedited order {order_id}: {e}")
        
        return updated_order
