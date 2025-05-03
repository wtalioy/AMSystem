from typing import Any, List
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException
from dbrm import Session

from app.services import worker_service
from app.api import deps
from app.schemas.log import Log
from app.schemas.user import Worker
from app.schemas.procedure import Procedure, ProcedureCreate

router = APIRouter()

@router.post("/logs", response_model=Log)
def create_maintenance_log(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Body(...),
    consumption: str = Body(...),
    cost: float = Body(...),
    duration: float = Body(...),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Create a maintenance log entry for an order
    """
    try:
        return worker_service.create_maintenance_log(
            db=db,
            worker_id=current_user.user_id,
            order_id=order_id,
            consumption=consumption,
            cost=Decimal(str(cost)),
            duration=Decimal(str(duration))
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/logs", response_model=List[Log])
def read_worker_logs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Retrieve logs created by the current worker
    """
    return worker_service.get_worker_logs(
        db=db, worker_id=current_user.user_id, skip=skip, limit=limit
    )


@router.get("/income", response_model=dict)
def calculate_worker_income(
    db: Session = Depends(deps.get_db),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Calculate the worker's income based on hours worked
    """
    try:
        return worker_service.calculate_worker_income(
            db=db, worker_id=current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/procedures/{procedure_id}", response_model=dict)
def update_procedure_status(
    *,
    db: Session = Depends(deps.get_db),
    procedure_id: int,
    new_status: int = Body(..., embed=True),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Update procedure status
    
    Status codes:
    - 0: pending
    - 1: in progress
    - 2: completed
    """
    success, procedure_obj, message = worker_service.update_procedure_status(
        db=db, procedure_id=procedure_id, new_status=new_status
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Return success result
    return {
        "success": True, 
        "procedure_id": procedure_id, 
        "new_status": new_status,
        "message": message,
        "procedure_text": procedure_obj.procedure_text if procedure_obj else ""
    }


@router.put("/procedures/batch", response_model=List[dict])
def batch_update_procedure_status(
    *,
    db: Session = Depends(deps.get_db),
    updates: List[dict] = Body(...),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Batch update multiple procedure statuses
    
    Request body format:
    ```
    [
      {"procedure_id": 1, "new_status": 2},
      {"procedure_id": 2, "new_status": 1},
      ...
    ]
    ```
    
    Status codes:
    - 0: pending
    - 1: in progress
    - 2: completed
    
    Notes:
    - Only procedures with status changes will be updated
    - Completed procedures cannot be changed to other statuses
    - Returns processing results for all procedures, including those that don't need updates
    """
    # Validate request body format
    if not updates:
        raise HTTPException(status_code=400, detail="Please provide a list of procedures to update")
    
    # Call service layer batch update function
    results = worker_service.batch_update_procedure_status(
        db=db, updates=updates
    )
    
    return results
