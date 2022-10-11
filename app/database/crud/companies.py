from typing import List

from app.database import models
from sqlalchemy.orm import Session

from app.database.schemas import CompanyCreate


def get_by_id(db: Session, company_id: int) -> models.Company:
    return db.query(models.Company).filter(models.Company.id == company_id).first()


def get_all_active(db: Session) -> List[models.Company]:
    return db.query(models.Company).filter(models.Company.is_active).all()


def get_all(db: Session) -> List[models.Company]:
    return db.query(models.Company).all()


def create(db: Session, company: CompanyCreate):
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def set_active(db: Session, company_id: int, state: bool):
    data = (
        db.query(models.Company)
        .filter(models.Company.id == company_id)
        .update({models.Company.is_active: state})
    )
    db.commit()
    return data
