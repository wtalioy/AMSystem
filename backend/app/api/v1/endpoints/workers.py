from typing import Any, List
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException
from app.dbrm import Session

from app.services import worker_service, procedure_service
from app.api import deps
from app.schemas import Log, Worker, OrderToWorker, OrderPending, Procedure

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


@router.get("/wage/rate", response_model=Decimal)
def get_worker_wage_rate(
    db: Session = Depends(deps.get_db),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Retrieve the wage rate for the current worker type
    """
    try:
        return worker_service.get_wage_rate(
            db=db, worker_type=current_user.worker_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wage/income", response_model=dict)
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
    

@router.get("/orders/owned", response_model=List[OrderToWorker])
def get_orders_for_worker(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Retrieve orders owned by the current worker
    """
    return worker_service.get_owner_orders(
        db=db, worker_id=current_user.user_id, skip=skip, limit=limit
    )


@router.get("/orders/pending", response_model=List[OrderPending])
def get_pending_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Retrieve all pending orders available for workers
    """
    return worker_service.get_pending_orders(
        db=db, skip=skip, limit=limit
    )


@router.post("/order/accept", response_model=Any)
def accept_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Body(...),
    procedures: list[str] = Body(...),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Accept an order and create procedures for it
    
    Request body format:
    ```
    {
      "order_id": "ORD123",
      "procedures": ["Check oil", "Replace filter", "Adjust brakes"]
    }
    ```
    
    Notes:
    - order_id: The order ID that all procedures will be associated with
    - procedures: A list of strings (one or more)
    """
    try:
        return procedure_service.create_procedures(
            db=db, order_id=order_id, procedures=procedures, worker_id=current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/order/procedures", response_model=List[Procedure])
def get_procedures_for_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str
) -> Any:
    """
    Retrieve all procedures for a specific order
    """
    return procedure_service.get_procedure_progress(db=db, order_id=order_id)


@router.put("/order/procedures", response_model=List[dict])
def update_procedure_status(
    *,
    db: Session = Depends(deps.get_db),
    updates: List[dict] = Body(...),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Update multiple procedure statuses
    
    Request body format:
    ```
    [
      {"procedure_id": 1, "status": 2},
      {"procedure_id": 2, "status": 1},
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
    results = procedure_service.update_procedure_status(
        db=db, updates=updates
    )
    
    return results
