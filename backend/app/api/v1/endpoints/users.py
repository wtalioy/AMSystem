from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from app.dbrm import Session

from app.services import user_service
from app.api import deps
from app.schemas import User, UserUpdate, CustomerCreate, WorkerCreate, AdminCreate

router = APIRouter()

@router.post("/register/customer", response_model=User)
def create_customer(
    *, db: Session = Depends(deps.get_db), customer_in: CustomerCreate
) -> Any:
    """
    Create new customer user
    """
    user = user_service.get_user_by_id(db, user_id=customer_in.user_id)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this ID already exists in the system",
        )
    return user_service.create_customer(db=db, customer_in=customer_in)


@router.post("/register/worker", response_model=User)
def create_worker(
    *,
    db: Session = Depends(deps.get_db),
    worker_in: WorkerCreate,
    current_user: User = Depends(deps.get_current_admin)
) -> Any:
    """
    Create new worker user (admin only)
    """
    user = user_service.get_user_by_id(db, user_id=worker_in.user_id)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this ID already exists in the system",
        )
    return user_service.create_worker(db=db, worker_in=worker_in)


@router.post("/register/admin", response_model=User)
def create_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: AdminCreate,
    current_user: User = Depends(deps.get_current_admin)
) -> Any:
    """
    Create new admin user (admin only)
    """
    user = user_service.get_user_by_id(db, user_id=admin_in.user_id)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this ID already exists in the system",
        )
    return user_service.create_admin(db=db, admin_in=admin_in)


@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user information
    """
    return user_service.update_user(db=db, user_id=current_user.user_id, user_in=user_in)


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific user by id
    """
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    if user.user_id != current_user.user_id and current_user.user_type != "administrator":
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return user


@router.get("/all", response_model=List[User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    """
    Retrieve users (admin only)
    """
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return users
