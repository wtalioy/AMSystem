from typing import List, Dict
from decimal import Decimal
from enum import IntEnum
from app.dbrm import Session

from app.crud import order, log, distribute, wage, worker
from app.schemas import LogCreate, Log, DistributeCreate, Distribute, OrderPending, OrderToWorker


class ProcedureStatus(IntEnum):
    PENDING = 0    # pending
    IN_PROGRESS = 1  # in progress
    COMPLETED = 2  # completed


def create_maintenance_log(
    db: Session, 
    worker_id: str, 
    order_id: str, 
    consumption: str,
    cost: Decimal,
    duration: Decimal
) -> Log:
    """Create a new maintenance log for an order"""
    order_obj = order.get_by_order_id(db, order_id=order_id)
    if not order_obj:
        raise ValueError("Order does not exist")
    
    # Create log entry
    log_in = LogCreate(
        consumption=consumption,
        cost=cost,
        duration=duration,
        order_id=order_id
    )
    return log.create_log_for_order(db=db, obj_in=log_in, worker_id=worker_id)


def get_worker_logs(
    db: Session, worker_id: str, skip: int = 0, limit: int = 100
) -> List[Log]:
    """Get all maintenance logs for a worker"""
    return log.get_logs_by_worker(db, worker_id=worker_id, skip=skip, limit=limit)


def get_owner_orders(
    db: Session, worker_id: str, skip: int = 0, limit: int = 100
) -> List[OrderToWorker]:
    """Get all orders owned by a worker"""
    return order.get_orders_by_worker(
        db, worker_id=worker_id, skip=skip, limit=limit
    )


def get_pending_orders(
    db: Session, skip: int = 0, limit: int = 100
) -> List[OrderPending]:
    """Get all pending orders for workers"""
    return order.get_pending_orders(
        db, skip=skip, limit=limit
    )


def get_wage_rate(db: Session, worker_type: int) -> Decimal:
    """Get the wage rate for a specific worker type"""
    wage_obj = wage.get_by_type(db, worker_type=worker_type)
    if not wage_obj:
        raise ValueError("No wage rate found for this worker type")
    
    return Decimal(str(wage_obj.wage_per_hour))


def calculate_worker_income(db: Session, worker_id: str) -> Dict:
    """Calculate a worker's total income based on their logs"""
    worker_obj = worker.get_by_id(db, worker_id=worker_id)
    if not worker_obj:
        raise ValueError("Worker does not exist")
    
    # Get wage rate
    wage_rate = wage.get_by_type(db, worker_type=worker_obj.worker_type)
    if not wage_rate:
        raise ValueError("No wage rate found for worker type")
    
    # Calculate total hours worked
    total_hours = log.get_total_duration_by_worker(db, worker_id=worker_id)
    
    # Calculate earnings
    hourly_rate = Decimal(str(wage_rate.wage_per_hour))
    earnings = total_hours * hourly_rate
    
    # Get already distributed amount
    distributed_amount = distribute.get_total_payment_for_worker(db, worker_id=worker_id)
    
    return {
        "worker_id": worker_id,
        "total_hours": total_hours,
        "hourly_rate": hourly_rate,
        "total_earnings": earnings,
        "paid_amount": distributed_amount,
        "pending_payment": earnings - distributed_amount
    }
