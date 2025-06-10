from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status, Response
from app.dbrm import Session

from app.api import deps
from app.services import CarService, OrderService
from app.schemas import User, OrderCreate, OrderToCustomer, OrderToAdmin
from app.core.enum import OrderStatus

router = APIRouter()

# Order CRUD operations
@router.post("/", response_model=OrderToCustomer, status_code=status.HTTP_201_CREATED)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: OrderCreate,
    current_user: User = Depends(deps.get_current_customer),
    response: Response
) -> Any:
    """
    Create a new repair order
    """
    # Verify the car belongs to the current customer
    car = CarService.get_car_by_id(db, car_id=order_in.car_id)
    if not car or car.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Car not found or does not belong to you",
        )
    
    try:
        audit_context = deps.get_audit_context(current_user)
        order = OrderService.create_order(
            db=db, obj_in=order_in, customer_id=current_user.user_id, audit_context=audit_context
        )
        # Add Location header for the newly created resource
        response.headers["Location"] = f"/api/v1/orders/order?order_id={order.order_id}"
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get("/", response_model=List[OrderToCustomer])
def get_owned_orders(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status_filter: Optional[int] = Query(None, description="Filter by order status"),
    current_user: User = Depends(deps.get_current_customer),
) -> Any:
    """
    Get owned orders (customer)
    """
    skip = (page - 1) * page_size
    
    return OrderService.get_customer_orders(
        db=db, customer_id=current_user.user_id, skip=skip, limit=page_size, status=status_filter
    )


@router.get("/all", response_model=List[OrderToAdmin])
def get_all_orders(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status_filter: Optional[int] = Query(None, description="Filter by order status"),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Get all orders with pagination and filtering (admin)
    """
    skip = (page - 1) * page_size
    
    return OrderService.get_all_orders(
        db=db, skip=skip, limit=page_size, status=status_filter
    )


# Order feedback
@router.post("/feedback", response_model=OrderToCustomer)
def add_order_feedback(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Body(...),
    rating: int = Body(..., ge=1, le=5),
    comment: Optional[str] = Body(None),
    current_user: User = Depends(deps.get_current_customer),
) -> Any:
    """
    Add customer feedback to a completed order
    """
    order = OrderService.get_order_by_id(db=db, order_id=order_id)
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
    if order.status != OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Order must be completed to add feedback"
        )

    audit_context = deps.get_audit_context(current_user)
    return OrderService.add_customer_feedback(
        db=db, order_id=order_id, rating=rating, comment=comment, audit_context=audit_context
    )


# Order expedite functionality  
@router.post("/expedite", response_model=OrderToCustomer)
def expedite_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: str = Body(...),
    current_user: User = Depends(deps.get_current_customer),
) -> Any:
    """
    Expedite an order - customer requests priority handling
    """
    order = OrderService.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    # Only the customer who owns the order can expedite it
    if order.customer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to expedite this order"
        )
    
    # Can only expedite non-completed orders
    if order.status >= 2:  # 2 = completed, 3 = cancelled
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Cannot expedite completed or cancelled orders"
        )

    audit_context = deps.get_audit_context(current_user)
    return OrderService.expedite_order(db=db, order_id=order_id, audit_context=audit_context)


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
    order = OrderService.get_order_by_id(db=db, order_id=order_id)
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
        if order.status > OrderStatus.ASSIGNED:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Only orders not started can be cancelled"
            )
    elif current_user.user_type != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to cancel or delete orders"
        )
    
    audit_context = deps.get_audit_context(current_user)
    OrderService.delete_order(db=db, order_id=order_id, audit_context=audit_context)
    return None