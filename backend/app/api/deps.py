from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from app.dbrm import Session, Engine

from app.core.config import settings
from app.schemas import TokenPayload, User, Customer, Worker, Admin
from app.services.user_service import get_user_by_id, get_typed_user_by_id

engine = Engine.from_env()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    with Session(engine) as session:
        yield session


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = get_user_by_id(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_customer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Customer:
    customer = get_typed_user_by_id(db=db, user_id=current_user.user_id, expected_type="customer")
    if not customer:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )
    return customer


def get_current_worker(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Worker:
    worker = get_typed_user_by_id(db=db, user_id=current_user.user_id, expected_type="worker")
    if not worker:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )
    return worker


def get_current_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Admin:
    admin = get_typed_user_by_id(db=db, user_id=current_user.user_id, expected_type="administrator")
    if not admin:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )
    return admin
