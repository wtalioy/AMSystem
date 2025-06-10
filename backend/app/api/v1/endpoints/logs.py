from typing import Any, List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dbrm import Session

from app.services import WorkerService
from app.api import deps
from app.schemas import Log, Worker, LogCreate

router = APIRouter()

@router.post("/", response_model=Log, status_code=status.HTTP_201_CREATED)
def create_maintenance_log(
    *,
    db: Session = Depends(deps.get_db),
    log_in: LogCreate,
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Create a maintenance log entry for an order by the current worker.
    """
    try:
        # This might need to be refactored to a generic log_service if logs are not worker-specific
        return WorkerService.create_maintenance_log(
            db=db, obj_in=log_in, worker_id=current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/", response_model=List[Log])
def get_worker_logs(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Get logs created by the current worker.
    """
    skip = (page - 1) * page_size
    # This might need to be refactored to a generic log_service
    return WorkerService.get_worker_logs(
        db=db, worker_id=current_user.user_id, skip=skip, limit=page_size
    )
