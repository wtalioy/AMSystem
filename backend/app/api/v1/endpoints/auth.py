from fastapi import APIRouter, Depends, HTTPException, status
from app.dbrm import Session

from app.api import deps
from app.core.database import get_db
from app.services import AuthService
from app.schemas import Token, User, UserLogin

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(
    *,
    db: Session = Depends(get_db),
    user_login: UserLogin
):
    """
    JSON-based token login endpoint, get an access token for future requests
    """
    user = AuthService.authenticate_user(
        db, user_name=user_login.user_name, password=user_login.user_pwd
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return AuthService.create_access_token(user_id=user.user_id)


@router.get("/verify", response_model=dict)
def verify_token(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Verify access token is valid and return user information
    """
    return {
        "user_id": current_user.user_id, 
        "user_type": current_user.user_type,
        "name": current_user.user_name,
        "is_active": True,
        "links": {
            "profile": f"/api/v1/users/me",
            "logout": f"/api/v1/auth/logout"
        }
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Logout the current user - client should discard the token
    
    In a stateless JWT system, the server doesn't store tokens, so this
    endpoint is provided as a standard way for clients to indicate logout action.
    The client should discard the token on successful response.
    
    For a production system, consider implementing token blacklisting or
    using shorter token lifetimes with refresh tokens.
    """
    # In a stateless JWT system, we don't actually invalidate the token here
    # This endpoint is provided for API consistency
    return None


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Refresh the current access token
    
    Gets a new token with extended expiration time.
    Using the current valid token as authentication.
    """
    return AuthService.create_access_token(user_id=current_user.user_id)
