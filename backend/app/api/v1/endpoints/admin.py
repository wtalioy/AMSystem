from typing import Any, List
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, services
from app.api import deps
from app.schemas.distribute import Distribute, DistributeCreate
from app.schemas.wage import Wage, WageCreate, WageUpdate

router = APIRouter()

@router.post("/wages", response_model=Wage)
def create_wage(
    *,
    db: Session = Depends(deps.get_db),
    wage_in: WageCreate,
    current_user: models.user.Administrator = Depends(deps.get_current_admin),
) -> Any:
    """
    Create new wage rate for a worker type
    """
    # Check if wage for this worker type already exists
    existing_wage = crud.wage.get_by_type(db, worker_type=wage_in.worker_type)
    if existing_wage:
        raise HTTPException(
            status_code=400,
            detail="Wage rate for this worker type already exists",
        )
    
    return crud.wage.create_wage(db=db, obj_in=wage_in)


@router.get("/wages", response_model=List[Wage])
def read_wages(
    db: Session = Depends(deps.get_db),
    current_user: models.user.Administrator = Depends(deps.get_current_admin),
) -> Any:
    """
    Retrieve all wage rates
    """
    return crud.wage.get_all_wages(db=db)


@router.put("/wages/{worker_type}", response_model=Wage)
def update_wage(
    *,
    db: Session = Depends(deps.get_db),
    worker_type: int,
    new_wage: int = Body(..., embed=True),
    current_user: models.user.Administrator = Depends(deps.get_current_admin),
) -> Any:
    """
    Update wage rate for a worker type
    """
    wage = crud.wage.get_by_type(db, worker_type=worker_type)
    if not wage:
        raise HTTPException(status_code=404, detail="Wage rate not found")
    
    return crud.wage.update_wage_rate(
        db=db, worker_type=worker_type, new_wage_per_hour=new_wage
    )


@router.post("/distribute-payment", response_model=Distribute)
def distribute_payment(
    *,
    db: Session = Depends(deps.get_db),
    worker_id: str = Body(...),
    amount: float = Body(...),
    current_user: models.user.Administrator = Depends(deps.get_current_admin),
) -> Any:
    """
    Record a payment distribution to a worker
    """
    try:
        return services.worker_service.distribute_payment(
            db=db, worker_id=worker_id, amount=Decimal(str(amount))
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics/car-types", response_model=List[dict])
def get_car_type_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.user.Administrator = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about car types, repairs, and costs
    """
    # This would be implemented with complex SQL queries in a real application
    # Here's a simplified placeholder
    from sqlalchemy import func, distinct
    
    # Get all car types
    car_types = db.query(distinct(models.car.Car.car_type)).all()
    
    result = []
    for car_type, in car_types:
        # Count cars of this type
        car_count = db.query(func.count(models.car.Car.car_id)).filter(
            models.car.Car.car_type == car_type
        ).scalar()
        
        # Count orders for cars of this type
        order_count = db.query(func.count(models.order.Order.order_id)).join(
            models.car.Car, models.car.Car.car_id == models.order.Order.car_id
        ).filter(
            models.car.Car.car_type == car_type
        ).scalar()
        
        # Calculate average cost
        cost_result = db.query(func.avg(models.log.Log.cost)).join(
            models.order.Order, models.order.Order.order_id == models.log.Log.order_id
        ).join(
            models.car.Car, models.car.Car.car_id == models.order.Order.car_id
        ).filter(
            models.car.Car.car_type == car_type
        ).scalar()
        
        avg_cost = float(cost_result) if cost_result else 0
        
        result.append({
            "car_type": car_type,
            "car_count": car_count,
            "repair_count": order_count,
            "average_repair_cost": avg_cost
        })
    
    return result


@router.get("/statistics/worker-types", response_model=List[dict])
def get_worker_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.user.Administrator = Depends(deps.get_current_admin),
) -> Any:
    """
    Get statistics about worker types, their tasks, and productivity
    """
    # This would be implemented with complex SQL queries in a real application
    # Here's a simplified placeholder
    from sqlalchemy import func, distinct
    
    # Get all worker types
    worker_types = db.query(distinct(models.user.Worker.worker_type)).all()
    
    result = []
    for worker_type, in worker_types:
        # Count workers of this type
        worker_count = db.query(func.count(models.user.Worker.user_id)).filter(
            models.user.Worker.worker_type == worker_type
        ).scalar()
        
        # Count logs/tasks for workers of this type
        task_count = db.query(func.count(models.log.Log.id)).join(
            models.user.Worker, models.user.Worker.user_id == models.log.Log.worker_id
        ).filter(
            models.user.Worker.worker_type == worker_type
        ).scalar()
        
        # Calculate total work hours
        hours_result = db.query(func.sum(models.log.Log.duration)).join(
            models.user.Worker, models.user.Worker.user_id == models.log.Log.worker_id
        ).filter(
            models.user.Worker.worker_type == worker_type
        ).scalar()
        
        total_hours = float(hours_result) if hours_result else 0
        
        # Get wage rate
        wage = crud.wage.get_by_type(db, worker_type=worker_type)
        wage_rate = wage.wage_per_hour if wage else 0
        
        result.append({
            "worker_type": worker_type,
            "worker_count": worker_count,
            "task_count": task_count,
            "total_work_hours": total_hours,
            "average_hours_per_task": total_hours / task_count if task_count > 0 else 0,
            "hourly_rate": wage_rate
        })
    
    return result


@router.get("/statistics/pending-orders", response_model=List[dict])
def get_pending_orders(
    db: Session = Depends(deps.get_db),
    current_user: models.user.Administrator = Depends(deps.get_current_admin),
) -> Any:
    """
    Get all pending orders and their details
    """
    pending_orders = db.query(models.order.Order).filter(
        models.order.Order.status < 2  # Status < 2 means not completed
    ).all()
    
    result = []
    for order in pending_orders:
        # Get car info
        car = crud.car.get_by_car_id(db, car_id=order.car_id)
        
        # Get procedures
        procedures = crud.procedure.get_procedures_by_order(db, order_id=order.order_id)
        
        # Calculate current progress
        completed_procedures = sum(1 for p in procedures if p.current_status == 2)
        total_procedures = len(procedures)
        progress = (completed_procedures / total_procedures * 100) if total_procedures > 0 else 0
        
        result.append({
            "order_id": order.order_id,
            "car_id": order.car_id,
            "car_type": car.car_type if car else None,
            "customer_id": order.customer_id,
            "start_time": order.start_time,
            "description": order.description,
            "status": order.status,
            "procedures_count": total_procedures,
            "completed_procedures": completed_procedures,
            "progress_percentage": progress
        })
    
    return result
