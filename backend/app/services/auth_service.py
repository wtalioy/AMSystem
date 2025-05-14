from datetime import timedelta
from typing import Optional
from app.dbrm import Session

from app.crud import user
from app.core import security
from app.core.config import settings
from app.schemas import Token, User


def authenticate_user(db: Session, user_name: str, password: str) -> Optional[User]:
    """
    Authenticate a user by checking username and password
    """
    user_obj = user.authenticate(db, user_name=user_name, password=password)
    if not user_obj:
        return None
    return user_obj


def create_access_token(user_id: str) -> Token:
    """
    Create an access token for the given user
    """
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user_id, expires_delta=expires_delta
    )
    return Token(access_token=access_token, token_type="bearer")
