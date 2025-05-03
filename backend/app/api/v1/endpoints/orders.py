from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from app.dbrm import Session

from app.api import deps
from app.services import car_service, order_service
from app.schemas.user import User, Customer
from app.schemas.order import Order, OrderCreate
from app.schemas.procedure import Procedure

router = APIRouter()

@router.post("/", response_model=Order)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: OrderCreate,
    current_user: Customer = Depends(deps.get_current_customer),
) -> Any:
    """
    Create new repair order
    """
    # Verify the car belongs to the current customer
    car = car_service.get_car_by_id(db, car_id=order_in.car_id)
    if not car or car.customer_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Car not found or does not belong to you",
        )
    
    try:
        order = order_service.create_order(
            db=db, obj_in=order_in, customer_id=current_user.id
        )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get("/", response_model=List[Order])
def read_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve orders.
    - If current user is customer, return their orders
    - If current user is an admin, return all orders
    """
    if current_user.user_type == "customer":
        return order_service.get_orders_for_customer(
            db=db, customer_id=current_user.id, skip=skip, limit=limit
        )
    elif current_user.user_type == "administrator":
        return order_service.get_all_orders(
            db=db, skip=skip, limit=limit
        )
    else:
        # Workers should use the worker-specific endpoints
        raise HTTPException(
            status_code=400,
            detail="Workers should use worker-specific endpoints",
        )


@router.get("/{order_id}", response_model=Order)
def read_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get order by ID.
    - If current user is customer, verify they own the order
    - If current user is admin, allow access to any order
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user.user_type == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return order


@router.put("/{order_id}/status", response_model=Order)
def update_order_status(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    new_status: int = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update order status
    - Workers can update status (accept work, mark as completed)
    - Admins can update any order status
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only workers and admins can update order status
    if current_user.user_type not in ["worker", "administrator"]:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return order_service.update_order_status(
        db=db, order_id=order_id, new_status=new_status
    )


@router.post("/{order_id}/feedback", response_model=Order)
def add_order_feedback(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    rating: int = Body(...),
    comment: str = Body(None),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add customer feedback to an order (rating and comment)
    """
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only the customer who owns the order can add feedback
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Order must be completed to add feedback
    if order.status != 2:  # 2 = completed
        raise HTTPException(status_code=400, detail="Order must be completed to add feedback")

    return order_service.add_customer_feedback(
        db=db, order_id=order_id, rating=rating, comment=comment
    )


@router.post("/{order_id}/procedures", response_model=Procedure)
def add_procedure(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    procedure_text: str = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add a repair procedure to an order
    """
    # Verify order exists
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only workers and admins can add procedures
    if current_user.user_type not in ["worker", "administrator"]:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return order_service.add_procedure_to_order(
        db=db, order_id=order_id, procedure_text=procedure_text
    )


@router.get("/{order_id}/cost", response_model=dict)
def calculate_order_cost(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Calculate the total cost for an order
    """
    # Verify order exists
    order = order_service.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions - customer can only check own orders
    if current_user.user_type == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return order_service.calculate_order_cost(db=db, order_id=order_id)
