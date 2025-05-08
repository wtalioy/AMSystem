from typing import Any, List, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status, Response
from app.dbrm import Session

from app.api import deps
from app.services import car_service, order_service, procedure_service
from app.schemas import User, Customer, Order, OrderCreate, Procedure

router = APIRouter()

# Order CRUD operations
@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: OrderCreate,
    current_user: Customer = Depends(deps.get_current_customer),
    response: Response
) -> Any:
    """
    Create a new repair order
    """
    # Verify the car belongs to the current customer
    car = car_service.get_car_by_id(db, car_id=order_in.car_id)
    if not car or car.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Car not found or does not belong to you",
        )
    
    try:
        order = order_service.create_order(
            db=db, obj_in=order_in, customer_id=current_user.user_id
        )
        # Add Location header for the newly created resource
        response.headers["Location"] = f"/api/v1/orders/{order.order_id}"
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get("/", response_model=List[Order])
def get_orders(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status_filter: Optional[int] = Query(None, description="Filter by order status"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get orders based on user role with pagination and filtering:
    - Customers: Get their own orders
    - Admins: Get all orders
    """
    skip = (page - 1) * page_size
    
    if current_user.user_type == "customer":
        return order_service.get_orders_for_customer(
            db=db, customer_id=current_user.user_id, skip=skip, limit=page_size,
            status=status_filter
        )
    elif current_user.user_type == "administrator":
        return order_service.get_all_orders(
            db=db, skip=skip, limit=page_size, status=status_filter
        )
    else:
        # Workers should use the worker-specific endpoints
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers should use worker-specific endpoints",
        )


@router.get("/{order_id}", response_model=Order)
def get_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific order by ID
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    if current_user.user_type == "customer" and order.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this order"
        )
    
    return order


# Order-related resources
@router.get("/{order_id}/procedures", response_model=List[Procedure])
def get_order_procedures(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all procedures associated with an order
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    if current_user.user_type == "customer" and order.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this order's procedures"
        )

    return procedure_service.get_procedure_progress(db=db, order_id=order_id)


# Order status updates
@router.patch("/{order_id}/status", response_model=Order)
def update_order_status(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    new_status: int = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update the status of an order
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    # Only workers and admins can update order status
    if current_user.user_type not in ["worker", "administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update order status"
        )

    try:
        return order_service.update_order_status(
            db=db, order_id=order_id, new_status=new_status
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


# Order feedback
@router.post("/{order_id}/feedback", response_model=Order)
def add_order_feedback(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    rating: int = Body(..., ge=1, le=5),
    comment: Optional[str] = Body(None),
    current_user: Customer = Depends(deps.get_current_customer),
) -> Any:
    """
    Add customer feedback to a completed order
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    # Only the customer who owns the order can add feedback
    if order.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to add feedback to this order"
        )
    
    # Order must be completed to add feedback
    if order.status != 2:  # 2 = completed
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Order must be completed to add feedback"
        )

    return order_service.add_customer_feedback(
        db=db, order_id=order_id, rating=rating, comment=comment
    )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> None:
    """
    Cancel or delete an order
    - Customers can only cancel their own pending orders
    - Admins can delete any order
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    # Check permissions
    if current_user.user_type == "customer":
        if order.customer_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not authorized to cancel this order"
            )
        # Customers can only cancel pending orders
        if order.status != 0:  # 0 = pending
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Only pending orders can be cancelled"
            )
    elif current_user.user_type != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to cancel or delete orders"
        )
    
    order_service.delete_order(db=db, order_id=order_id)
    return None