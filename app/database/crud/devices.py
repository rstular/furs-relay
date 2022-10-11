from typing import List, Optional
from app.database.crud import premises

from app.database.models import Device
from sqlalchemy import update
from sqlalchemy.orm import Session, joinedload


def get_by_id(db: Session, device_id: int) -> Optional[Device]:
    return db.query(Device).filter(Device.id == device_id).first()


def get_by_id_with_premise(db: Session, device_id) -> Optional[Device]:
    return (
        db.query(Device)
        .options(joinedload(Device.premise))
        .filter(Device.id == device_id)
        .first()
    )


def get_all_for_company(db: Session, company_id: int) -> List[Device]:
    company_premises = premises.get_all_for_company(db, company_id)
    return (
        db.query(Device)
        .filter(Device.premise_id.in_([p.id for p in company_premises]))
        .all()
    )
    # return db.query(Device).filter(Device.company_id == company_id).all()


def get_all(db: Session) -> List[Device]:
    return db.query(Device).all()


def set_active(db: Session, device_id: int, state: bool):
    data = (
        db.query(Device)
        .filter(Device.id == device_id)
        .update({Device.is_active: state})
    )
    db.commit()
    return data


def get_inc_id(db: Session, device_id: int) -> int:
    stmt = (
        update(Device)
        .where(Device.id == device_id)
        .values(seq_invoice_id=Device.seq_invoice_id + 1)
        .returning(Device.seq_invoice_id)
    )
    ret = db.execute(stmt).fetchall()[0][0]
    db.commit()
    return ret
