from typing import Any, List, Optional
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from app.dbrm import Session

from app.services import worker_service, procedure_service
from app.api import deps
from app.schemas import Log, Worker, OrderToWorker, OrderPending, Procedure

router = APIRouter()

# Worker maintenance logs
@router.post("/logs", response_model=Log, status_code=status.HTTP_201_CREATED)
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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/logs", response_model=List[Log])
def get_worker_logs(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Get logs created by the current worker
    """
    skip = (page - 1) * page_size
    return worker_service.get_worker_logs(
        db=db, worker_id=current_user.user_id, skip=skip, limit=page_size
    )


# Worker wage information
@router.get("/wage-rate", response_model=Decimal)
def get_worker_wage_rate(
    *,
    db: Session = Depends(deps.get_db),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Get the hourly wage rate for the current worker
    """
    try:
        return worker_service.get_wage_rate(
            db=db, worker_type=current_user.worker_type
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/income", response_model=dict)
def get_worker_income(
    *,
    db: Session = Depends(deps.get_db),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Get the worker's calculated income based on hours worked
    """
    try:
        return worker_service.calculate_worker_income(
            db=db, worker_id=current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    

# Worker order management
@router.get("/orders", response_model=List[OrderToWorker])
def get_assigned_orders(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status: Optional[int] = Query(None, description="Filter by order status"),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Get orders assigned to the current worker
    """
    skip = (page - 1) * page_size
    return worker_service.get_owner_orders(
        db=db, worker_id=current_user.user_id, skip=skip, limit=page_size, status=status
    )


@router.get("/available-orders", response_model=List[OrderPending])
def get_available_orders(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Get all available orders that workers can accept
    """
    skip = (page - 1) * page_size
    return worker_service.get_pending_orders(
        db=db, skip=skip, limit=page_size
    )


@router.post("/orders/{order_id}/accept", response_model=Any)
def accept_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    procedures: list[str] = Body(...),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Accept an order and create procedures for it
    
    Request body format:
    ```
    {
      "procedures": ["Check oil", "Replace filter", "Adjust brakes"]
    }
    ```
    """
    try:
        return procedure_service.create_procedures(
            db=db, order_id=order_id, procedures=procedures, worker_id=current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    

@router.get("/orders/{order_id}/procedures", response_model=List[Procedure])
def get_order_procedures(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    current_user: Worker = Depends(deps.get_current_worker)
) -> Any:
    """
    Get all procedures for a specific order
    """
    return procedure_service.get_procedure_progress(db=db, order_id=order_id)


@router.patch("/procedures", response_model=List[dict])
def update_procedures(
    *,
    db: Session = Depends(deps.get_db),
    updates: List[dict] = Body(...),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Update the status of multiple procedures
    
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
    """
    # Validate request body format
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please provide a list of procedures to update"
        )
    
    # Call service layer batch update function
    try:
        results = procedure_service.update_procedure_status(
            db=db, updates=updates
        )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
