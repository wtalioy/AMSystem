from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from app.dbrm import Session

from app.api import deps
from app.services import car_service
from app.schemas import Car, CarCreate, CarUpdate, User, Customer

router = APIRouter()

@router.post("/", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(
    *,
    db: Session = Depends(deps.get_db),
    car_in: CarCreate,
    current_user: Customer = Depends(deps.get_current_customer),
    response: Response
) -> Any:
    """
    Register a new car for the current customer
    """
    if car_service.get_car_by_id(db, car_id=car_in.car_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The car with this ID already exists in the system",
        )
    car = car_service.create_car(
        db=db, obj_in=car_in, customer_id=current_user.user_id
    )
    
    # Add Location header for the newly created resource
    response.headers["Location"] = f"/api/v1/cars/{car.car_id}"
    return car


@router.get("/", response_model=List[Car])
def get_cars(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get cars based on user role:
    - Customers: Get their own cars
    - Admins: Get all cars in the system
    """
    skip = (page - 1) * page_size
    
    if current_user.user_type == "customer":
        return car_service.get_customer_cars(
            db=db, customer_id=current_user.user_id,
            skip=skip, limit=page_size
        )
    elif current_user.user_type == "administrator":
        return car_service.get_all_cars(
            db=db, skip=skip, limit=page_size
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list cars"
        )


@router.get("/{car_id}", response_model=Car)
def get_car(
    *,
    db: Session = Depends(deps.get_db),
    car_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific car by ID
    """
    car = car_service.get_car_by_id(db=db, car_id=car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Car not found"
        )
    
    if current_user.user_type == "customer" and car.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this car"
        )
    
    return car


@router.put("/{car_id}", response_model=Car)
def update_car(
    *,
    db: Session = Depends(deps.get_db),
    car_id: str,
    car_in: CarUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update car information (full update)
    """
    car = car_service.get_car_by_id(db=db, car_id=car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Car not found"
        )
    
    # Only owner or admin can update car
    if current_user.user_type == "customer" and car.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update this car"
        )
    elif current_user.user_type == "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers cannot update car information"
        )
    
    return car_service.update_car(
        db=db, car_id=car_id, obj_in=car_in
    )


@router.patch("/{car_id}", response_model=Car)
def partial_update_car(
    *,
    db: Session = Depends(deps.get_db),
    car_id: str,
    car_in: Dict[str, Any],
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Partially update car information
    """
    car = car_service.get_car_by_id(db=db, car_id=car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Car not found"
        )
    
    # Only owner or admin can update car
    if current_user.user_type == "customer" and car.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update this car"
        )
    elif current_user.user_type == "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers cannot update car information"
        )
    
    return car_service.partial_update_car(
        db=db, car_id=car_id, obj_in=car_in
    )


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    *,
    db: Session = Depends(deps.get_db),
    car_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> None:
    """
    Delete a car
    """
    car = car_service.get_car_by_id(db=db, car_id=car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Car not found"
        )
    
    # Only owner or admin can delete car
    if current_user.user_type == "customer" and car.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to delete this car"
        )
    elif current_user.user_type == "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers cannot delete cars"
        )
    
    car_service.delete_car(db=db, car_id=car_id)
    return None


@router.get("/{car_id}/maintenance-history", response_model=List[Dict[str, Any]])
def get_car_maintenance_history(
    *,
    db: Session = Depends(deps.get_db),
    car_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get the maintenance history for a specific car
    """
    # Calculate pagination parameters
    skip = (page - 1) * page_size
    
    # Verify car exists
    car = car_service.get_car_by_id(db=db, car_id=car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Car not found"
        )
    
    # Check permissions
    if current_user.user_type == "customer" and car.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this car's history"
        )

    return car_service.get_car_maintenance_history(
        db=db, car_id=car_id, skip=skip, limit=page_size
    )
