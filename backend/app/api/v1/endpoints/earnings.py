from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from app.dbrm import Session

from app.services.earnings_service import EarningsService
from app.schedulers.earning_scheduler import get_scheduler
from app.api import deps
from app.schemas import (
    Admin, WorkerMonthlyEarnings, FailedEarningsCalculation, 
    MonthlyDistributionResults, EarningsReport
)

router = APIRouter()


@router.get("/{worker_id}/monthly", response_model=WorkerMonthlyEarnings)
def get_worker_monthly_earnings(
    *,
    db: Session = Depends(deps.get_db),
    worker_id: str = Path(..., description="Worker ID"),
    year: int = Query(..., description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get monthly earnings calculation for a specific worker (Admin only)
    """
    try:
        earnings = EarningsService.calculate_worker_monthly_earnings(
            db=db, worker_id=worker_id, year=year, month=month
        )
        return earnings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{worker_id}/history", response_model=List[WorkerMonthlyEarnings])
def get_worker_earnings_history(
    *,
    db: Session = Depends(deps.get_db),
    worker_id: str = Path(..., description="Worker ID"),
    months_back: int = Query(12, ge=1, le=24, description="Number of months back to retrieve"),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get earnings history for a worker (Admin only)
    """
    try:
        history = EarningsService.get_worker_earnings_history(
            db=db, worker_id=worker_id, months_back=months_back
        )
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve earnings history: {str(e)}"
        )


@router.get("/all-workers/monthly", response_model=List[Union[WorkerMonthlyEarnings, FailedEarningsCalculation]])
def get_all_workers_monthly_earnings(
    *,
    db: Session = Depends(deps.get_db),
    year: int = Query(..., description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get monthly earnings for all workers (Admin only)
    """
    try:
        earnings = EarningsService.calculate_all_workers_monthly_earnings(
            db=db, year=year, month=month
        )
        return earnings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate earnings for all workers: {str(e)}"
        )


@router.get("/summary-report", response_model=EarningsReport)
def get_earnings_summary_report(
    *,
    db: Session = Depends(deps.get_db),
    year: int = Query(..., description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get earnings summary report for all workers in a month (Admin only)
    """
    try:
        report = EarningsService.get_earnings_summary_report(
            db=db, year=year, month=month
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate earnings report: {str(e)}"
        )


@router.post("/distribute/monthly", response_model=MonthlyDistributionResults)
def run_monthly_distribution(
    *,
    db: Session = Depends(deps.get_db),
    year: int = Query(..., description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Manually trigger monthly earnings distribution for all workers (Admin only)
    """
    try:
        scheduler = get_scheduler()
        result = scheduler.run_earnings_distribution_now(year=year, month=month)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run earnings distribution: {str(e)}"
        )


@router.get("/scheduler/status", response_model=Dict)
def get_scheduler_status(
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get current scheduler status (Admin only)
    """
    try:
        scheduler = get_scheduler()
        return scheduler.get_scheduler_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )


@router.post("/scheduler/start", response_model=Dict)
def start_scheduler(
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Start the earnings scheduler (Admin only)
    """
    try:
        scheduler = get_scheduler()
        scheduler.start()
        return {"message": "Scheduler started", "status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/scheduler/stop", response_model=Dict)
def stop_scheduler(
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Stop the earnings scheduler (Admin only)
    """
    try:
        scheduler = get_scheduler()
        scheduler.stop()
        return {"message": "Scheduler stopped", "status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop scheduler: {str(e)}"
        ) 