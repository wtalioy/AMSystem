from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import services
from app.api import deps
from app.schemas.token import Token

router = APIRouter()

@router.post("/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = services.auth_service.authenticate_user(
        db, user_id=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return services.auth_service.create_access_token(user_id=user.id)


@router.post("/test-token", response_model=dict)
def test_token(current_user = Depends(deps.get_current_user)):
    """
    Test access token
    """
    return {"user_id": current_user.id, "user_type": current_user.user_type}
