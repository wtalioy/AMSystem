from typing import Any, List, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from app.dbrm import Session

from app.services import user_service
from app.api import deps
from app.schemas import User, UserUpdate, CustomerCreate, WorkerCreate, AdminCreate, Admin

router = APIRouter()

# Register endpoints organized by user type
@router.post("/customers", response_model=User, status_code=status.HTTP_201_CREATED)
def create_customer(
    *, 
    db: Session = Depends(deps.get_db), 
    customer_in: CustomerCreate,
    response: Response
) -> Any:
    """
    Register a new customer
    """
    user = user_service.get_user_by_name(db, user_name=customer_in.user_name)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this name already exists in the system",
        )
    created_customer_orm = user_service.create_customer(db=db, customer_in=customer_in)
    
    # Add Location header for the newly created resource
    response.headers["Location"] = f"/api/v1/users/{created_customer_orm.user_id}"
    
    user_to_return = user_service.get_user_by_id(db, user_id=created_customer_orm.user_id)
    
    if not user_to_return:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve user details after creation."
        )
        
    return user_to_return


@router.post("/workers", response_model=User, status_code=status.HTTP_201_CREATED)
def create_worker(
    *,
    db: Session = Depends(deps.get_db),
    worker_in: WorkerCreate,
    current_user: User = Depends(deps.get_current_admin),
    response: Response
) -> Any:
    """
    Register a new worker (admin only)
    """
    user = user_service.get_user_by_id(db, user_id=worker_in.user_id)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this ID already exists in the system",
        )
    worker = user_service.create_worker(db=db, worker_in=worker_in)
    
    # Add Location header for the newly created resource
    response.headers["Location"] = f"/api/v1/users/{worker.user_id}"
    return worker


@router.post("/admins", response_model=User, status_code=status.HTTP_201_CREATED)
def create_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: AdminCreate,
    current_user: User = Depends(deps.get_current_admin),
    response: Response
) -> Any:
    """
    Register a new admin (admin only)
    """
    user = user_service.get_user_by_id(db, user_id=admin_in.user_id)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this ID already exists in the system",
        )
    admin = user_service.create_admin(db=db, admin_in=admin_in)
    
    # Add Location header for the newly created resource
    response.headers["Location"] = f"/api/v1/users/{admin.user_id}"
    return admin


# Current user profile management
@router.get("/me", response_model=User)
def get_current_user(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user profile
    """
    return current_user


@router.put("/me", response_model=User)
def update_current_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update current user profile (full update)
    """
    return user_service.update_user(db=db, user_id=current_user.user_id, user_in=user_in)


@router.patch("/me", response_model=User)
def partial_update_current_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: Dict[str, Any],
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Partially update current user profile
    """
    return user_service.partial_update_user(db=db, user_id=current_user.user_id, obj_in=user_in)


# Admin operations on users
@router.get("/{user_id}", response_model=User)
def get_user_by_id(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get a specific user by ID (admin only)
    """
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    return user


@router.get("/", response_model=List[User])
def get_users(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get all users (admin only) with pagination
    """
    skip = (page - 1) * page_size
    users = user_service.get_all_users(db, skip=skip, limit=page_size)
    return users


@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Update a specific user (admin only)
    """
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    return user_service.update_user(db=db, user_id=user_id, user_in=user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    current_user: Admin = Depends(deps.get_current_admin),
) -> None:
    """
    Delete a specific user (admin only)
    """
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    user_service.delete_user(db=db, user_id=user_id)
    return None
