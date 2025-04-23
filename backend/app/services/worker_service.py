from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from decimal import Decimal

from app import crud
from app.schemas.log import LogCreate
from app.schemas.distribute import DistributeCreate
from app.models.log import Log
from app.models.distribute import Distribute

def create_maintenance_log(
    db: Session, 
    worker_id: str, 
    order_id: str, 
    consumption: str,
    cost: Decimal,
    duration: Decimal
) -> Log:
    """Create a new maintenance log for an order"""
    # Verify the order exists
    order = crud.order.get_by_order_id(db, order_id=order_id)
    if not order:
        raise ValueError("Order does not exist")
    
    # Create log entry
    log_in = LogCreate(
        consumption=consumption,
        cost=cost,
        duration=duration,
        order_id=order_id
    )
    return crud.log.create_log_for_order(db=db, obj_in=log_in, worker_id=worker_id)

def get_worker_logs(
    db: Session, worker_id: str, skip: int = 0, limit: int = 100
) -> List[Log]:
    """Get all maintenance logs for a worker"""
    return crud.log.get_logs_by_worker(db, worker_id=worker_id, skip=skip, limit=limit)

def calculate_worker_income(db: Session, worker_id: str) -> Dict:
    """Calculate a worker's total income based on their logs"""
    # Get worker information
    worker = crud.worker.get_by_id(db, worker_id=worker_id)
    if not worker:
        raise ValueError("Worker does not exist")
    
    # Get wage rate
    wage_rate = crud.wage.get_by_type(db, worker_type=worker.worker_type)
    if not wage_rate:
        raise ValueError("No wage rate found for worker type")
    
    # Calculate total hours worked
    total_hours = crud.log.get_total_duration_by_worker(db, worker_id=worker_id)
    
    # Calculate earnings
    hourly_rate = Decimal(str(wage_rate.wage_per_hour))
    earnings = total_hours * hourly_rate
    
    # Get already distributed amount
    distributed = crud.distribute.get_total_payment_for_worker(db, worker_id=worker_id)
    
    return {
        "worker_id": worker_id,
        "total_hours": total_hours,
        "hourly_rate": hourly_rate,
        "total_earnings": earnings,
        "paid_amount": distributed,
        "pending_payment": earnings - distributed
    }

def distribute_payment(db: Session, worker_id: str, amount: Decimal) -> Distribute:
    """Record a payment distribution to a worker"""
    # Verify worker exists
    worker = crud.worker.get_by_id(db, worker_id=worker_id)
    if not worker:
        raise ValueError("Worker does not exist")
    
    # Create distribution
    distribute_in = DistributeCreate(
        amount=amount,
        worker_id=worker_id
    )
    return crud.distribute.create_distribution(db=db, obj_in=distribute_in)

def update_procedure_status(db: Session, procedure_id: int, new_status: int) -> bool:
    """Update the status of a procedure"""
    procedure = crud.procedure.update_procedure_status(
        db=db, procedure_id=procedure_id, new_status=new_status
    )
    return procedure is not None
