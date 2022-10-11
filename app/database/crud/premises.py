from typing import List
from sqlalchemy.orm import Session

from app.database.models import BusinessPremise


def get_all_for_company(db: Session, company_id: int) -> List[BusinessPremise]:
    return (
        db.query(BusinessPremise).filter(BusinessPremise.company_id == company_id).all()
    )


def get_all(db: Session) -> List[BusinessPremise]:
    return db.query(BusinessPremise).all()
