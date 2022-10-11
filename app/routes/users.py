from typing import List

from app.database import get_db
from app.database.crud import users
from app.database.models import UserRole
from app.database.schemas import User
from app.util.auth import ActiveUserWithRole
from app.util.datatypes import ActionResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/list", summary="Get a list of all users", response_model=List[User])
async def get_users(
    db: Session = Depends(get_db),
    user: User = Depends(
        ActiveUserWithRole([UserRole.ORGANIZATION_ADMIN, UserRole.ADMIN])
    ),
):
    return users.get_by_company_id(db, user.company_id)


@router.get("/list/all", summary="Get a list of all users", response_model=List[User])
async def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(ActiveUserWithRole([UserRole.ADMIN])),
):
    return users.get_all(db)


@router.delete("/delete/{user_id}", summary="Delete a user")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(
        ActiveUserWithRole([UserRole.ADMIN, UserRole.ORGANIZATION_ADMIN])
    ),
):
    target_user = users.get_by_id(db, user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if target_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not delete other admins",
        )

    if target_user.company_id != user.company_id and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete users in your own company",
        )

    users.delete(db, user_id)

    return ActionResponse(success=True)
