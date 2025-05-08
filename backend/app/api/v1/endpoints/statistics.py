from typing import Any, List

from fastapi import APIRouter, Depends
from app.dbrm import Session

from app.services import admin_service
from app.api import deps
from app.schemas import Admin

router = APIRouter()

@router.get("/cars", response_model=List[dict])
def get_car_statistics(
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about car types, repairs, and costs
    """
    return admin_service.get_car_type_statistics(db)


@router.get("/workers", response_model=List[dict])
def get_worker_statistics(
    *,
    db: Session = Depends(deps.get_db),
    start_time: str,
    end_time: str,
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about worker types, their tasks, and productivity
    """
    return admin_service.get_worker_statistics(db, start_time=start_time, end_time=end_time)


@router.get("/incomplete-orders", response_model=List[dict])
def get_incomplete_orders_statistics(
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about incomplete orders
    """
    return admin_service.get_incomplete_orders_statistics(db)
