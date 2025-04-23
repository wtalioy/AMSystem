from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, services
from app.api import deps
from app.schemas.car import Car, CarCreate, CarUpdate

router = APIRouter()

@router.post("/", response_model=Car)
def create_car(
    *,
    db: Session = Depends(deps.get_db),
    car_in: CarCreate,
    current_user: models.user.Customer = Depends(deps.get_current_customer),
) -> Any:
    """
    Create new car for current customer
    """
    if crud.car.get_by_car_id(db, car_id=car_in.car_id):
        raise HTTPException(
            status_code=400,
            detail="The car with this ID already exists in the system",
        )
    return services.car_service.create_car(
        db=db, obj_in=car_in, customer_id=current_user.user_id
    )


@router.get("/", response_model=List[Car])
def read_cars(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve cars.
    - If current user is a customer, return only their cars
    - If current user is an administrator, return all cars
    """
    if current_user.user_type == "customer":
        return services.car_service.get_customer_cars(
            db=db, customer_id=current_user.id
        )
    elif current_user.user_type == "administrator":
        return services.car_service.get_all_cars(
            db=db, skip=skip, limit=limit
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="No permission to list cars"
        )


@router.get("/{car_id}", response_model=Car)
def read_car(
    *,
    db: Session = Depends(deps.get_db),
    car_id: str,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get car by ID.
    - If current user is a customer, verify they own the car
    - If current user is an administrator, allow access to any car
    """
    car = services.car_service.get_car_by_id(db=db, car_id=car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    if current_user.user_type == "customer" and car.customer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return car


@router.put("/{car_id}", response_model=Car)
def update_car(
    *,
    db: Session = Depends(deps.get_db),
    car_id: str,
    car_in: CarUpdate,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a car.
    """
    car = services.car_service.get_car_by_id(db=db, car_id=car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Only owner or admin can update car
    if current_user.user_type == "customer" and car.customer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    elif current_user.user_type == "worker":
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return services.car_service.update_car(
        db=db, car_id=car_id, obj_in=car_in
    )


@router.get("/{car_id}/maintenance-history", response_model=List[dict])
def read_car_maintenance_history(
    *,
    db: Session = Depends(deps.get_db),
    car_id: str,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get maintenance history for a car
    """
    # Verify car exists
    car = services.car_service.get_car_by_id(db=db, car_id=car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Check permissions
    if current_user.user_type == "customer" and car.customer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return services.car_service.get_car_maintenance_history(db=db, car_id=car_id)
