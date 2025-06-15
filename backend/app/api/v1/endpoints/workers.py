from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dbrm import Session

from app.api import deps
from app.core.database import get_db
from app.services import WorkerService, EarningsService
from app.schemas import User, OrderToWorker, WorkerMonthlyEarnings

router = APIRouter()

@router.post("/orders/{order_id}/accept")
def accept_order(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    current_user: User = Depends(deps.get_current_worker),
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
    db: Session = Depends(get_db),
    order_id: str,
    current_user: User = Depends(deps.get_current_worker),
) -> Any:
    """
    Reject an assigned order - will trigger automatic reassignment
    """
    try:
        result = WorkerService.reject_order(
            db=db, order_id=order_id, worker_id=current_user.user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
@router.post("/orders/{order_id}/complete")
def complete_order(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    current_user: User = Depends(deps.get_current_worker),
) -> Any:
    """
    Complete an assigned order
    """
    try:
        result = WorkerService.complete_order(
            db=db, order_id=order_id, worker_id=current_user.user_id
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
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(deps.get_current_worker),
) -> Any:
    """
    Get orders assigned to the current worker
    """
    skip = (page - 1) * page_size
    return WorkerService.get_assigned_orders(
        db=db, worker_id=current_user.user_id, skip=skip, limit=page_size
    )

    
@router.get("/my-earnings/monthly", response_model=WorkerMonthlyEarnings)
def get_my_monthly_earnings(
    *,
    db: Session = Depends(get_db),
    year: int = Query(..., description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    current_user: User = Depends(deps.get_current_worker),
) -> Any:
    """
    Get monthly earnings for the current worker
    """
    try:
        earnings = EarningsService.calculate_worker_monthly_earnings(
            db=db, worker_id=current_user.user_id, year=year, month=month
        )
        return earnings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get("/my-earnings/history", response_model=List[WorkerMonthlyEarnings])
def get_my_earnings_history(
    *,
    db: Session = Depends(get_db),
    months_back: int = Query(12, ge=1, le=24, description="Number of months back to retrieve"),
    current_user: User = Depends(deps.get_current_worker),
) -> Any:
    """
    Get earnings history for the current worker
    """
    try:
        history = EarningsService.get_worker_earnings_history(
            db=db, worker_id=current_user.user_id, months_back=months_back
        )
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve earnings history: {str(e)}"
        )