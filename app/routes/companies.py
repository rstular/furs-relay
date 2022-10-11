from sqlite3 import IntegrityError
from typing import List

from app.database import get_db
from app.database.crud import companies
from app.database.models import UserRole
from app.database.schemas import Company, CompanyCreate, User
from app.util.auth import ActiveUserWithRole
from app.util.datatypes import ActionResponse
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.errors import UniqueViolation
from sqlalchemy.orm import Session

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get(
    "/list", summary="Get a list of all companies", response_model=List[Company]
)
async def get_companies(
    _: User = Depends(ActiveUserWithRole([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    return companies.get_all(db)


@router.post(
    "/create",
    summary="Create a new company entry",
    response_model=Company,
    status_code=201,
)
async def create_company(
    company: CompanyCreate,
    _: User = Depends(ActiveUserWithRole([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    try:
        created_company = companies.create(db, company)
    except IntegrityError | UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate company information",
        )
    return created_company


@router.post(
    "/disable/{company_id}",
    summary="Disable a company",
    response_model=ActionResponse,
)
async def disable_company(
    company_id: int,
    _: User = Depends(ActiveUserWithRole([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    if companies.set_active(db, company_id, False) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found",
        )
    return ActionResponse(success=True)


@router.post(
    "/enable/{company_id}",
    summary="Enable a company",
    response_model=ActionResponse,
)
async def enable_company(
    company_id: int,
    _: User = Depends(ActiveUserWithRole([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    if companies.set_active(db, company_id, True) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found",
        )
    return ActionResponse(success=True)
