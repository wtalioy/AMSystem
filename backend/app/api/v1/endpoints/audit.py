from typing import List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from app.dbrm import Session

from app.api import deps
from app.core.database import get_db
from app.services import AuditService
from app.schemas.audit_log import AuditLog, AuditLogSummary
from app.schemas import Admin

router = APIRouter()

@router.get("/summary", response_model=AuditLogSummary)
def get_change_summary(
    *,
    db: Session = Depends(get_db),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get summary of changes in a date range (Admin only)
    """
    # Default to last 30 days if no dates provided
    if not start_date:
        start_dt = datetime.now() - timedelta(days=30)
    else:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    
    if not end_date:
        end_dt = datetime.now()
    else:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )
    
    if start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after end_date"
        )
    
    return AuditService.get_change_summary(db, start_dt, end_dt)


@router.get("/recent", response_model=List[AuditLog])
def get_recent_changes(
    *,
    db: Session = Depends(get_db),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get recent changes within specified hours (Admin only)
    """
    skip = (page - 1) * page_size
    recent_changes = AuditService.get_recent_changes(db, hours, skip, page_size)
    return recent_changes


@router.post("/rollback", response_model=dict)
def get_rollback_data(
    *,
    db: Session = Depends(get_db),
    target_audit_id: str = Body(..., embed=True),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get rollback data for a specific audit point (Admin only)
    Note: This returns the data needed for rollback, actual rollback should be done manually
    """
    rollback_data = AuditService.rollback_to_version(db, target_audit_id)
    
    if not rollback_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rollback point not found or no data available"
        )
    
    return {
        "target_audit_id": target_audit_id,
        "rollback_data": rollback_data,
        "note": "Use this data to manually restore the record to this state"
    }