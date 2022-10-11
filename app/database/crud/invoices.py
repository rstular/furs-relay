from typing import List

from app.database import models, schemas
from sqlalchemy.orm import Session


def create(db: Session, invoice: schemas.InvoiceCreate) -> models.Invoice:
    db_invoice = models.Invoice(
        zoi=invoice.zoi,
        eor=invoice.eor,
        invoice_number=invoice.invoice_number,
        issued_at=invoice.issued_at,
        total=invoice.total,
        user_id=invoice.user_id,
        company_id=invoice.company_id,
        device_id=invoice.device_id,
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def get_by_id(db: Session, invoice_id: int) -> models.Invoice:
    return db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()


def get_by_company_id(db: Session, company_id: int) -> List[models.Invoice]:
    return (
        db.query(models.Invoice).filter(models.Invoice.company_id == company_id).all()
    )


def get_all(db: Session) -> List[models.Invoice]:
    return db.query(models.Invoice).all()
