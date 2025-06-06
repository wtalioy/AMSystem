from typing import Any, List, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from app.dbrm import Session

from app.services import UserService
from app.api import deps
from app.schemas import User, UserUpdate, UserCreate, Customer, Worker, Admin

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    response: Response
) -> Any:
    """
    Register a new user
    """
    user = UserService.get_user_by_name(db, user_name=user_in.user_name)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this name already exists in the system",
        )
    created_user = UserService.create_user(db=db, obj_in=user_in)
    
    # Add Location header for the newly created resource
    response.headers["Location"] = f"/api/v1/users/{created_user.user_id}"

    return created_user


# Current user profile management
@router.get("/me", response_model=Union[Customer, Worker, Admin, User])
def get_current_user(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user profile with complete information based on user type
    """
    complete_user = UserService.get_user_by_id(db, user_id=current_user.user_id, typed=True)
    if not complete_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return complete_user


@router.put("/me", response_model=User, deprecated=True)
def update_current_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update current user profile (full update)
    """
    return User


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
    audit_context = deps.get_audit_context(current_user)
    return UserService.partial_update_user(db=db, user_id=current_user.user_id, obj_in=user_in, audit_context=audit_context)


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
    user = UserService.get_user_by_id(db, user_id=user_id)
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
    users = UserService.get_all_users(db, skip=skip, limit=page_size)
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
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    audit_context = deps.get_audit_context(current_user)
    return UserService.update_user(db=db, user_id=user_id, user_in=user_in, audit_context=audit_context)


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
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    audit_context = deps.get_audit_context(current_user)
    UserService.delete_user(db=db, user_id=user_id, audit_context=audit_context)
    return None
