from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.core import security
from app.core.config import settings
from app.schemas.token import Token
from app.models.user import User


def authenticate_user(db: Session, user_id: str, password: str) -> Optional[User]:
    """
    Authenticate a user by checking username and password
    """
    user = crud.user.authenticate(db, user_id=user_id, password=password)
    if not user:
        return None
    return user


def create_access_token(user_id: str) -> Token:
    """
    Create an access token for the given user
    """
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user_id, expires_delta=expires_delta
    )
    return Token(access_token=access_token, token_type="bearer")
