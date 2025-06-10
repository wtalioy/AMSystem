from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from app.dbrm import Session

from app.services import ProcedureService, OrderService
from app.api import deps
from app.schemas import Procedure, User, ProcedureCreate, ProcedureUpdate

router = APIRouter()

@router.post("/", response_model=List[Procedure], status_code=status.HTTP_201_CREATED)
def create_order_procedures(
    *,
    db: Session = Depends(deps.get_db),
    procedures: List[ProcedureCreate],
    current_user: User = Depends(deps.get_current_worker),
) -> Any:
    """
    Create procedures for an order
    """
    try:
        return ProcedureService.create_procedures(
            db=db, procedures=procedures, worker_id=current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/", response_model=List[Procedure])
def get_order_procedures(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Query(..., description="Order ID to get procedures for"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all procedures associated with an order
    """
    order = OrderService.get_order_by_id(db=db, order_id=order_id)
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

    return ProcedureService.get_procedure_progress(db=db, order_id=order_id)


@router.patch("/", response_model=List[Procedure])
def update_procedure_status(
    *,
    db: Session = Depends(deps.get_db),
    procedures: List[ProcedureUpdate] = Body(...),
    current_user: User = Depends(deps.get_current_worker),
) -> Any:
    """
    Update the status of multiple procedures
    """
    if not procedures:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please provide a list of procedures to update"
        )
    try:
        results = ProcedureService.update_procedure_status(
            db=db, procedure_updates=procedures, worker_id=current_user.user_id
        )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
