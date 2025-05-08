from typing import Any, List, Optional
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from app.dbrm import Session

from app.services import worker_service, wage_service
from app.api import deps
from app.schemas import Worker, Wage, WageCreate, Admin

router = APIRouter()

# Worker wage information
@router.get("/worker-wage-rate", response_model=Decimal)
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

# Wage management
@router.post("/", response_model=Wage) # Root path for /wages
def create_wage_rate(
    *,
    db: Session = Depends(deps.get_db),
    wage_in: WageCreate,
    current_user: Admin = Depends(deps.get_current_admin), # Assuming Admin dependency
) -> Any:
    """
    Create a new wage rate for a worker type
    """
    existing_wage = wage_service.get_wage_by_worker_type(db, worker_type=wage_in.worker_type)
    if existing_wage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wage rate for this worker type already exists",
        )
    return wage_service.create_wage(db=db, obj_in=wage_in)


@router.get("/", response_model=List[Wage])
def get_wage_rates(
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin), # Assuming Admin dependency
) -> Any:
    """
    Get all wage rates
    """
    return wage_service.get_all_wages(db=db)


@router.put("/", response_model=Wage)
def update_wage_rate(
    *,
    db: Session = Depends(deps.get_db),
    worker_type: int = Query(...),
    new_wage: int = Body(..., embed=True), # Assuming new_wage is an int based on original
    current_user: Admin = Depends(deps.get_current_admin), # Assuming Admin dependency
) -> Any:
    """
    Update wage rate for a worker type
    """
    wage = wage_service.get_wage_by_worker_type(db, worker_type=worker_type)
    if not wage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wage rate not found")
    return wage_service.update_wage_rate(
        db=db, worker_type=worker_type, new_wage_per_hour=new_wage
    )
