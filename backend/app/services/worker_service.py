from typing import List, Dict, Union, Any
from decimal import Decimal
from enum import IntEnum
from app.dbrm import Session

from app.crud import order, log, distribute, procedure, wage, worker
from app.schemas import LogCreate, Log, DistributeCreate, Distribute, Procedure, ProcedureCreate


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


def distribute_payment(db: Session, worker_id: str, amount: Decimal) -> Distribute:
    """Record a payment distribution to a worker"""
    # Verify worker exists
    worker_obj = worker.get_by_id(db, worker_id=worker_id)
    if not worker_obj:
        raise ValueError("Worker does not exist")
    
    # Create distribution
    distribute_in = DistributeCreate(
        amount=amount,
        worker_id=worker_id
    )
    return distribute.create_distribution(db=db, obj_in=distribute_in)


def create_procedures(
    db: Session, 
    order_id: str, 
    procedures: Any
) -> Union[Procedure, List[Procedure]]:
    """ Create maintenance procedures for an order """
    # Verify order exists
    order_obj = order.get_by_order_id(db, order_id=order_id)
    if not order_obj:
        raise ValueError(f"Order with ID {order_id} does not exist")
    
    if not procedures:
        raise ValueError("Please provide at least one procedure")
        
    procedure_objects = []
    for proc_item in procedures:
        # Handle both string and dict formats
        if isinstance(proc_item, dict):
            procedure_text = proc_item.get("procedure_text")
        else:
            procedure_text = proc_item
        
        # Validate required fields
        if not procedure_text:
            raise ValueError("Missing procedure text")
        
        # Create procedure object with default status (0: pending)
        procedure_in = ProcedureCreate(
            order_id=order_id,
            procedure_text=procedure_text,
            current_status=ProcedureStatus.PENDING
        )
        procedure_objects.append(procedure_in)
    
    return procedure.create_procedures(db=db, order_id=order_id, procedures=procedure_objects)


def update_procedure_status(
    db: Session, 
    updates: List[Dict[str, int]]
) -> List[Dict]:
    """ Update the status of procedures """
    results = []
    to_update = []  # List of procedures to update
    status_names = {
        ProcedureStatus.PENDING: "pending",
        ProcedureStatus.IN_PROGRESS: "in progress",
        ProcedureStatus.COMPLETED: "completed"
    }
    
    # Step 1: Check each procedure, only process those that need status changes
    for update_info in updates:
        procedure_id = update_info.get("procedure_id")
        new_status = update_info.get("status")
        
        # Check required fields
        if procedure_id is None or new_status is None:
            results.append({
                "procedure_id": procedure_id,
                "success": False,
                "message": "Missing required information: procedure_id or status",
                "procedure_text": None
            })
            continue
        
        # Get procedure information
        procedure_obj = procedure.get_by_id(db, procedure_id=procedure_id)
        if not procedure_obj:
            results.append({
                "procedure_id": procedure_id,
                "success": False,
                "message": "Procedure not found",
                "procedure_text": None
            })
            continue
            
        # Validate status code
        if new_status not in [st.value for st in ProcedureStatus]:
            results.append({
                "procedure_id": procedure_id,
                "success": False,
                "message": f"Invalid status value: {new_status}, valid values are: 0 (pending), 1 (in progress), 2 (completed)",
                "procedure_text": procedure_obj.procedure_text
            })
            continue
        
        current_status = procedure_obj.current_status
        
        # If status hasn't changed, skip this procedure
        if current_status == new_status:
            results.append({
                "procedure_id": procedure_id,
                "success": True,
                "new_status": new_status,
                "message": "Procedure status unchanged, no update needed",
                "procedure_text": procedure_obj.procedure_text
            })
            continue
            
        # Check status transition validity: completed procedures can't change status
        if current_status == ProcedureStatus.COMPLETED and new_status != ProcedureStatus.COMPLETED:
            results.append({
                "procedure_id": procedure_id,
                "success": False,
                "message": "Completed procedures cannot be changed to other statuses",
                "procedure_text": procedure_obj.procedure_text
            })
            continue
            
        # If validation passes and status needs to change, add to update list
        to_update.append({
            "procedure_id": procedure_id,
            "new_status": new_status,
            "current_status": current_status,
            "procedure_text": procedure_obj.procedure_text
        })
    
    # Step 2: Batch update procedures that need status changes
    if to_update:
        update_data = [{"procedure_id": u["procedure_id"], "new_status": u["new_status"]} for u in to_update]
        updated_procedures = procedure.update_procedure_status(db=db, updates=update_data)
        
        # Process update results
        for i, proc in enumerate(updated_procedures):
            update_info = to_update[i]
            if proc:
                results.append({
                    "procedure_id": update_info["procedure_id"],
                    "success": True,
                    "new_status": update_info["new_status"],
                    "message": f"Procedure status changed from '{status_names[update_info['current_status']]}' to '{status_names[update_info['new_status']]}'",
                    "procedure_text": update_info["procedure_text"]
                })
            else:
                results.append({
                    "procedure_id": update_info["procedure_id"],
                    "success": False,
                    "message": "Status update failed",
                    "procedure_text": update_info["procedure_text"]
                })
    
    return results
