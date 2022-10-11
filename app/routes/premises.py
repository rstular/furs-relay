from typing import List

from app.database import get_db
from app.database.crud import premises
from app.database.models import UserRole
from app.database.schemas import BusinessPremise, User
from app.util.auth import ActiveUserWithRole, get_current_active_user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/premises", tags=["premises"])


@router.get(
    "/list",
    summary="Get a list of all premises for your company",
    response_model=List[BusinessPremise],
)
async def get_premises(
    user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    return premises.get_all_for_company(db, user.company_id)


@router.get(
    "/list/all",
    summary="Get a list of all premises",
    response_model=List[BusinessPremise],
)
async def get_all_premises(
    _: User = Depends(ActiveUserWithRole([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    return premises.get_all(db)
