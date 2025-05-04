from typing import Any, List
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException
from app.dbrm import Session

from app.api import deps
from app.services import wage_service, worker_service, order_service
from app.schemas import Wage, WageCreate, Distribute, Admin
from backend.app.services import admin_service

router = APIRouter()

@router.get("/cost", response_model=dict)
def calculate_order_cost(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Body(...),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Calculate the total cost for an order
    """
    # Verify order exists
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions - customer can only check own orders
    if current_user.user_type == "customer" and order.customer_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return order_service.calculate_order_cost(db=db, order_id=order_id)


@router.post("/wage/rate", response_model=Wage)
def create_wage(
    *,
    db: Session = Depends(deps.get_db),
    wage_in: WageCreate,
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Create new wage rate for a worker type
    """
    # Check if wage for this worker type already exists
    existing_wage = wage_service.get_wage_by_worker_type(db, worker_type=wage_in.worker_type)
    if existing_wage:
        raise HTTPException(
            status_code=400,
            detail="Wage rate for this worker type already exists",
        )

    return wage_service.create_wage(db=db, obj_in=wage_in)


@router.get("/wage/rate", response_model=List[Wage])
def read_wages(
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Retrieve all wage rates
    """
    return wage_service.get_all_wages(db=db)


@router.put("/wage/rate/{worker_type}", response_model=Wage)
def update_wage(
    *,
    db: Session = Depends(deps.get_db),
    worker_type: int,
    new_wage: int = Body(..., embed=True),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Update wage rate for a worker type
    """
    wage = wage_service.get_wage_by_worker_type(db, worker_type=worker_type)
    if not wage:
        raise HTTPException(status_code=404, detail="Wage rate not found")

    return wage_service.update_wage_rate(
        db=db, worker_type=worker_type, new_wage_per_hour=new_wage
    )


@router.get("/wage/distribute", response_model=List[Distribute])
def get_all_distributions(
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Retrieve all payment distributions to workers
    """
    return admin_service.get_all_distributions(db=db)


@router.post("/wage/distribute", response_model=Distribute)
def distribute_payment(
    *,
    db: Session = Depends(deps.get_db),
    worker_id: str = Body(...),
    amount: float = Body(...),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Record a payment distribution to a worker
    """
    try:
        return worker_service.distribute_payment(
            db=db, worker_id=worker_id, amount=Decimal(str(amount))
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics/car-types", response_model=List[dict])
def get_car_type_statistics(
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about car types, repairs, and costs
    """
    return admin_service.get_car_type_statistics(db)


@router.get("/statistics/worker-types", response_model=List[dict])
def get_worker_statistics(
    db: Session = Depends(deps.get_db),
    start_time: str = Body(...),
    end_time: str = Body(...),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about worker types, their tasks, and productivity
    """
    return admin_service.get_worker_statistics(db, start_time=start_time, end_time=end_time)


@router.get("/statistics/orders/incomplete", response_model=List[dict])
def get_incomplete_orders(
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get all incomplete orders and their details
    """
    return admin_service.get_incomplete_orders_statistics(db)
