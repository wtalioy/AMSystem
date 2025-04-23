from typing import Any, List
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, services
from app.api import deps
from app.models.log import Log
from app.models.procedure import Procedure

router = APIRouter()

@router.post("/logs", response_model=Log)
def create_maintenance_log(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Body(...),
    consumption: str = Body(...),
    cost: float = Body(...),
    duration: float = Body(...),
    current_user: models.user.Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Create a maintenance log entry for an order
    """
    try:
        return services.worker_service.create_maintenance_log(
            db=db,
            worker_id=current_user.user_id,
            order_id=order_id,
            consumption=consumption,
            cost=Decimal(str(cost)),
            duration=Decimal(str(duration))
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/logs", response_model=List[Log])
def read_worker_logs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.user.Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Retrieve logs created by the current worker
    """
    return services.worker_service.get_worker_logs(
        db=db, worker_id=current_user.user_id, skip=skip, limit=limit
    )


@router.get("/income", response_model=dict)
def calculate_worker_income(
    db: Session = Depends(deps.get_db),
    current_user: models.user.Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Calculate the worker's income based on hours worked
    """
    try:
        return services.worker_service.calculate_worker_income(
            db=db, worker_id=current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/procedures/{procedure_id}", response_model=dict)
def update_procedure_status(
    *,
    db: Session = Depends(deps.get_db),
    procedure_id: int,
    new_status: int = Body(..., embed=True),
    current_user: models.user.Worker = Depends(deps.get_current_worker),
) -> Any:
    """
    Update a repair procedure status
    """
    # Verify procedure exists
    procedure = crud.procedure.get_by_id(db, procedure_id=procedure_id)
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    # Update the status
    success = services.worker_service.update_procedure_status(
        db=db, procedure_id=procedure_id, new_status=new_status
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update procedure status")
        
    return {"success": True, "procedure_id": procedure_id, "new_status": new_status}
