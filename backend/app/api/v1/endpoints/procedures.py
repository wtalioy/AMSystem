from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from app.dbrm import Session

from app.services import procedure_service, order_service
from app.api import deps
from app.schemas import Procedure, Worker, User

router = APIRouter()

@router.post("/", response_model=Any)
def accept_order_for_worker(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Query(..., description="Order ID to accept and create procedures for"),
    procedures: list[str] = Body(...),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Accept an order and create procedures for it (moved from workers.py)
    
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


@router.get("/", response_model=List[Procedure]) # Was /procedures in workers.py
def get_order_procedures(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Query(..., description="Order ID to get procedures for"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all procedures associated with an order
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    if current_user.user_type == "customer" and order.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this order's procedures"
        )

    return procedure_service.get_procedure_progress(db=db, order_id=order_id)


@router.patch("/", response_model=List[dict]) # Was /procedures in workers.py
def update_procedure_status(
    *,
    db: Session = Depends(deps.get_db),
    updates: List[dict] = Body(...),
    current_user: Worker = Depends(deps.get_current_worker), # Assuming only a worker can update
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
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please provide a list of procedures to update"
        )
    try:
        # Add any necessary authorization checks here, e.g., ensuring the worker is assigned to these procedures.
        results = procedure_service.update_procedure_status(
            db=db, updates=updates # Potentially pass current_user.user_id for validation in service
        )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
