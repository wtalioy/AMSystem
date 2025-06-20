from typing import Any, List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from app.dbrm import Session

from app.core.database import get_db
from app.services import WorkerService, WageService
from app.api import deps
from app.schemas import Worker, Wage, WageCreate, Admin, WageUpdate

router = APIRouter()

# Worker wage information
@router.get("/worker-wage-rate", response_model=Decimal)
def get_worker_wage_rate(
    *,
    db: Session = Depends(get_db),
    current_user: Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Get the hourly wage rate for the current worker
    """
    try:
        return WorkerService.get_wage_rate(
            db=db, worker_type=current_user.worker_type
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Wage management
@router.post("/", response_model=Wage, status_code=status.HTTP_201_CREATED)
def create_wage_rate(
    *,
    db: Session = Depends(get_db),
    wage_in: WageCreate,
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Create a new wage rate for a worker type
    """
    existing_wage = WageService.get_wage_by_worker_type(db, worker_type=wage_in.worker_type)
    if existing_wage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wage rate for this worker type already exists",
        )
    return WageService.create_wage(db=db, obj_in=wage_in)


@router.get("/", response_model=List[Wage])
def get_wage_rates(
    db: Session = Depends(get_db),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get all wage rates
    """
    return WageService.get_all_wages(db=db)


@router.put("/", response_model=Wage)
def update_wage_rate(
    *,
    db: Session = Depends(get_db),
    wage_in: WageUpdate,
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Update wage rate for a worker type
    """
    wage = WageService.get_wage_by_worker_type(db, worker_type=wage_in.worker_type)
    if not wage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wage rate not found")
    return WageService.update_wage_rate(
        db=db, worker_type=wage_in.worker_type, new_wage_per_hour=wage_in.wage_per_hour
    )
