from typing import Optional, List, Dict, Any
from app.dbrm import Session
from decimal import Decimal

from app.crud import order, car, log, procedure, worker, wage
from app.schemas import Order, OrderCreate, Procedure, ProcedureCreate, OrderToCustomer, OrderToAdmin


def create_order(db: Session, obj_in: OrderCreate, customer_id: str) -> OrderCreate:
    """Create a new repair order"""
    # Verify the car belongs to the customer
    car_obj = car.get_by_car_id(db, car_id=obj_in.car_id)
    if not car_obj or car_obj.customer_id != customer_id:
        raise ValueError("Car does not exist or does not belong to customer")
    
    # Create the order
    return OrderCreate.model_validate(
        order.create_order_for_customer(db=db, obj_in=obj_in, customer_id=customer_id)
    )


def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
    """Get a specific order by ID"""
    return Order.model_validate(
        order.get_by_order_id(db, order_id=order_id)
    )


def get_orders_for_customer(
    db: Session, customer_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None
) -> List[OrderToCustomer]:
    """
    Get all orders for a customer with pagination and optional status filtering
    """
    orders = order.get_orders_by_customer(
        db, customer_id=customer_id, skip=skip, limit=limit, status=status
    )
    orders = [OrderToCustomer.model_validate(o) for o in orders]
    return orders


def get_all_orders(
    db: Session, skip: int = 0, limit: int = 100, status: Optional[int] = None
) -> List[OrderToAdmin]:
    """
    Get all orders with pagination and optional status filtering (admin function)
    """
    orders = order.get_multi_with_details(db, skip=skip, limit=limit, status=status)
    orders = [OrderToAdmin.model_validate(o) for o in orders]
    return orders


def update_order_status(db: Session, order_id: str, new_status: int) -> Optional[Order]:
    """
    Update the status of an order
    
    Status codes:
    0 - Pending
    1 - In Progress
    2 - Completed
    3 - Cancelled
    
    Raises ValueError if the status transition is invalid
    """
    order_obj = order.get_by_order_id(db, order_id=order_id)
    if not order_obj:
        return None
    
    # Validate status transition
    if new_status not in [0, 1, 2, 3]:
        raise ValueError(f"Invalid status code: {new_status}")
    
    # Check for valid transitions
    current_status = order_obj.status
    
    # Cannot change from completed or cancelled to other statuses
    if current_status == 2 and new_status != 2:
        raise ValueError("Cannot change status of a completed order")
    
    if current_status == 3 and new_status != 3:
        raise ValueError("Cannot change status of a cancelled order")
    
    # Update the status
    return Order.model_validate(order.update_status(db, order_id=order_id, new_status=new_status))


def add_customer_feedback(
    db: Session, order_id: str, rating: int, comment: Optional[str] = None
) -> Optional[OrderToCustomer]:
    """Add customer feedback to an order"""
    return OrderToCustomer.model_validate(
        order.add_customer_feedback(db=db, order_id=order_id, rating=rating, comment=comment)
    )


def add_procedure_to_order(
    db: Session, order_id: str, procedure_text: str
) -> Procedure:
    """Add a repair procedure to an order"""
    procedure_in = ProcedureCreate(
        order_id=order_id,
        procedure_text=procedure_text,
        current_status=0  # Initially pending
    )
    return Procedure.model_validate(
        procedure.create_procedure_for_order(db=db, obj_in=procedure_in)
    )


def delete_order(db: Session, order_id: str) -> bool:
    """
    Delete an order from the database
    
    Returns True if order was deleted, False if order was not found
    
    Note: This will also delete all associated procedures and logs due to
    database cascade delete constraints
    """
    order_obj = order.get_by_order_id(db, order_id=order_id)
    if not order_obj:
        return False
    
    order.remove(db, id=order_obj.id)
    return True


def calculate_order_cost(db: Session, order_id: str) -> Dict:
    """Calculate the total cost for an order (material cost + labor cost)"""
    # Get all logs for this order
    logs = log.get_logs_by_order(db, order_id=order_id)
    
    # Calculate material cost
    material_cost = sum(log_entry.cost for log_entry in logs)
    
    # Calculate labor cost
    labor_cost = Decimal('0.0')
    for log_entry in logs:
        worker_obj = worker.get_by_id(db, worker_id=log_entry.worker_id)
        if worker_obj:
            wage_rate = wage.get_by_type(db, worker_type=worker_obj.worker_type)
            if wage_rate:
                labor_cost += log_entry.duration * Decimal(str(wage_rate.wage_per_hour))
    
    return {
        "order_id": order_id,
        "material_cost": material_cost,
        "labor_cost": labor_cost,
        "total_cost": material_cost + labor_cost
    }
