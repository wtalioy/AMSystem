from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from decimal import Decimal

from app import crud
from app.schemas.order import OrderCreate, OrderUpdate
from app.schemas.procedure import ProcedureCreate
from app.models.order import Order
from app.models.log import Log
from app.models.procedure import Procedure


def create_order(db: Session, obj_in: OrderCreate, customer_id: str) -> Order:
    """Create a new repair order"""
    # Verify the car belongs to the customer
    car = crud.car.get_by_car_id(db, car_id=obj_in.car_id)
    if not car or car.customer_id != customer_id:
        raise ValueError("Car does not exist or does not belong to customer")
    
    # Create the order
    return crud.order.create_order_for_customer(
        db=db, obj_in=obj_in, customer_id=customer_id
    )


def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
    """Get a specific order by ID"""
    return crud.order.get_by_order_id(db, order_id=order_id)


def get_orders_for_customer(
    db: Session, customer_id: str, skip: int = 0, limit: int = 100
) -> List[Order]:
    """Get all orders for a customer"""
    return crud.order.get_orders_by_customer(
        db, customer_id=customer_id, skip=skip, limit=limit
    )


def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders (admin function)"""
    return crud.order.get_multi(db, skip=skip, limit=limit)


def update_order_status(db: Session, order_id: str, new_status: int) -> Optional[Order]:
    """Update the status of an order"""
    return crud.order.update_order_status(
        db=db, order_id=order_id, new_status=new_status
    )


def add_customer_feedback(
    db: Session, order_id: str, rating: int, comment: Optional[str] = None
) -> Optional[Order]:
    """Add customer feedback to an order"""
    return crud.order.add_customer_feedback(
        db=db, order_id=order_id, rating=rating, comment=comment
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
    return crud.procedure.create_procedure_for_order(db=db, obj_in=procedure_in)


def calculate_order_cost(db: Session, order_id: str) -> Dict:
    """Calculate the total cost for an order (material cost + labor cost)"""
    # Get all logs for this order
    logs = crud.log.get_logs_by_order(db, order_id=order_id)
    
    # Calculate material cost
    material_cost = sum(log.cost for log in logs)
    
    # Calculate labor cost
    labor_cost = Decimal('0.0')
    for log in logs:
        worker = crud.worker.get_by_id(db, worker_id=log.worker_id)
        if worker:
            wage_rate = crud.wage.get_by_type(db, worker_type=worker.worker_type)
            if wage_rate:
                labor_cost += log.duration * Decimal(str(wage_rate.wage_per_hour))
    
    return {
        "order_id": order_id,
        "material_cost": material_cost,
        "labor_cost": labor_cost,
        "total_cost": material_cost + labor_cost
    }
