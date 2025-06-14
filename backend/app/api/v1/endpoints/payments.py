from typing import Any, List
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, status
from app.dbrm import Session

from app.api import deps
from app.core.database import get_db
from app.services import AdminService
from app.schemas import Distribute, Admin

router = APIRouter()


# Payment distributions (Admin only)
@router.get("/", response_model=List[Distribute])
def get_payment_distributions(
    db: Session = Depends(get_db),
    current_user: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    Get all payment distributions to workers. (Admin only)
    """
    return AdminService.get_all_distributions(db=db)


@router.post("/", response_model=Distribute, status_code=status.HTTP_201_CREATED)
def create_payment_distribution(
    *,
    db: Session = Depends(get_db),
    worker_id: str = Body(...),
    amount: float = Body(...),
    current_user: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    Record a payment distribution to a worker. (Admin only)
    """
    try:
        return AdminService.distribute_payment(
            db=db, worker_id=worker_id, amount=Decimal(str(amount))
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
