from dataclasses import dataclass
from datetime import timedelta

from app.database import get_db
from app.database.crud import users
from app.database.schemas import User
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from app.util.auth import create_access_token, get_current_active_user
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


@dataclass
class TokenResponse:
    access_token: str
    token_type: str


@router.post(
    "/token", summary="Login to obtain an access token", response_model=TokenResponse
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = users.get_by_username(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    try:
        PasswordHasher().verify(user.password, form_data.password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    summary="Get information about the currently logged in user",
    response_model=User,
)
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user
