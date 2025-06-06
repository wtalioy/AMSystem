from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from app.dbrm import Session

from app.api import deps
from app.services import WorkerService
from app.schemas import Worker, OrderToWorker

router = APIRouter()

@router.post("/orders/{order_id}/accept")
def accept_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Accept an assigned order
    """
    try:
        result = WorkerService.accept_order(
            db=db, order_id=order_id, worker_id=current_user.user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.post("/orders/{order_id}/reject")
def reject_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    reason: Optional[str] = Body(None, embed=True),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Reject an assigned order - will trigger automatic reassignment
    """
    try:
        result = WorkerService.reject_order(
            db=db, order_id=order_id, worker_id=current_user.user_id, reason=reason
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.get("/orders/assigned", response_model=List[OrderToWorker])
def get_assigned_orders(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status_filter: Optional[int] = Query(None, description="Filter by order status"),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Get orders assigned to the current worker
    """
    skip = (page - 1) * page_size
    return WorkerService.get_assigned_orders(
        db=db, worker_id=current_user.user_id, skip=skip, limit=page_size, status=status_filter
    )

@router.get("/earnings")
def get_worker_earnings(
    *,
    db: Session = Depends(deps.get_db),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Calculate worker's earnings for specified period
    """
    try:
        return WorkerService.calculate_worker_earnings(
            db=db, worker_id=current_user.user_id, start_date=start_date, end_date=end_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) 