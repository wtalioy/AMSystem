from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Query
from app.dbrm import Session

from app.core.database import get_db
from app.services import AdminService, OrderService
from app.api import deps
from app.schemas import (
    User,
    OrderToAdmin,
    CarTypeStatistics,
    CostAnalysisByPeriod,
    NegativeFeedbackAnalysis,
    WorkerProductivityAnalysis,
    WorkerStatistics,
    IncompleteOrderStatistics,
)

router = APIRouter()

@router.get("/orders", response_model=List[OrderToAdmin])
def get_orders(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status_filter: Optional[int] = Query(None, description="Filter by order status"),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Get orders with pagination and filtering:
    """
    skip = (page - 1) * page_size
    
    return OrderService.get_all_orders(
        db=db, skip=skip, limit=page_size, status=status_filter
    )


@router.get("/cars", response_model=List[CarTypeStatistics])
def get_car_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about car types, repairs, and costs
    """
    return AdminService.get_car_type_statistics(db)


@router.get("/costs/analysis", response_model=CostAnalysisByPeriod)
def get_cost_analysis(
    *,
    db: Session = Depends(get_db),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    period_type: str = Query("month", description="Period type: month or quarter"),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Get cost analysis by time period with labor vs materials breakdown
    """
    return AdminService.get_cost_analysis_by_period(
        db, start_date=start_date, end_date=end_date, period_type=period_type
    )


@router.get("/feedback/negative", response_model=NegativeFeedbackAnalysis)
def get_negative_feedback_analysis(
    *,
    db: Session = Depends(get_db),
    rating_threshold: int = Query(3, ge=1, le=5, description="Rating threshold (orders below this rating)"),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Analyze orders with low ratings and associated worker performance
    """
    return AdminService.get_negative_feedback_analysis(db, rating_threshold=rating_threshold)


@router.get("/workers/productivity", response_model=List[WorkerProductivityAnalysis])
def get_worker_productivity_analysis(
    *,
    db: Session = Depends(get_db),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Analyze worker productivity metrics by specialty
    """
    return AdminService.get_worker_productivity_analysis(
        db, start_date=start_date, end_date=end_date
    )


@router.get("/workers", response_model=List[WorkerStatistics])
def get_worker_statistics(
    *,
    db: Session = Depends(get_db),
    start_time: str,
    end_time: str,
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about worker types, their tasks, and productivity
    """
    return AdminService.get_worker_statistics(db, start_time=start_time, end_time=end_time)


@router.get("/incomplete-orders", response_model=List[IncompleteOrderStatistics])
def get_incomplete_orders_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about incomplete orders
    """
    return AdminService.get_incomplete_orders_statistics(db)
