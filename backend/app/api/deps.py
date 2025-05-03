from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from app.dbrm import Session, Engine

from app import crud, schemas
from app.core.config import settings
from app.schemas.token import TokenPayload

engine = Engine.from_env()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    with Session(engine) as session:
        yield session


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> schemas.user.User:
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
    user = crud.user.get_by_id(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_customer(
    current_user: schemas.user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.user.Customer:
    if current_user.user_type != "customer":
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )
    return crud.customer.get_by_id(db=db, customer_id=current_user.id)


def get_current_worker(
    current_user: schemas.user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.user.Worker:
    if current_user.user_type != "worker":
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )
    return crud.worker.get_by_id(db=db, worker_id=current_user.id)


def get_current_admin(
    current_user: schemas.user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.user.Admin:
    if current_user.user_type != "administrator":
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )
    return crud.admin.get_by_id(db=db, admin_id=current_user.id)
