from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

import pytz
from app.database import get_db, models, schemas
from app.database.crud import companies, devices, invoices
from app.util.auth import ActiveUserWithRole, get_current_active_user
from app.util.certificates import CompanyAPI, get_api_for_company
from app.util.invoices import generate_invoice_number
from fastapi import APIRouter, Depends, HTTPException
from furs_fiscal.api import TaxesPerSeller
from loguru import logger
from sqlalchemy.orm import Session

router = APIRouter(prefix="/invoices", tags=["invoices"])


@dataclass
class InvoiceResponse:
    internal_id: int
    invoice_number: str
    zoi: str
    eor: str
    issued_at: datetime


@dataclass
class PriceEntry:
    amount: Decimal
    tax_rate: Decimal


@dataclass
class Invoice:
    device_id: int
    operator_tax_id: int
    prices: List[PriceEntry]
    issued_at: Optional[datetime] = None


@router.post(
    "/create",
    summary="Create & issue an invoice",
    status_code=201,
    response_model=InvoiceResponse,
)
async def create_invoice(
    invoice: Invoice,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Verify that the provided device is active
    device: models.Device = devices.get_by_id_with_premise(db, invoice.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    elif not device.is_active:
        raise HTTPException(status_code=403, detail="Device not active")

    # Verify that device and user belong to the same company
    if user.company_id != device.premise.company_id:
        raise HTTPException(status_code=403, detail="Device not owned by company")

    # Verify that the company is active
    company = companies.get_by_id(db, user.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    elif not company.is_active:
        raise HTTPException(status_code=403, detail="Company not active")

    seq_id = devices.get_inc_id(db, invoice.device_id)
    company_api: CompanyAPI = get_api_for_company(user.company_id)

    subsequent_submit = not invoice.issued_at is None
    if invoice.issued_at is None:
        invoice.issued_at = datetime.now(tz=pytz.UTC)

    total_invoice_amount = sum(price.amount for price in invoice.prices)

    zoi = company_api.api.calculate_zoi(
        company.tax_id,
        invoice.issued_at,
        str(seq_id),
        device.premise.furs_id,
        device.device_id,
        total_invoice_amount,
    )

    seller_one = TaxesPerSeller(
        other_taxes_amount=None,
        exempt_vat_taxable_amount=None,
        reverse_vat_taxable_amount=None,
        non_taxable_amount=None,
        special_tax_rules_amount=None,
        seller_tax_number=None,
    )

    for price in invoice.prices:
        seller_one.add_vat_amount(
            float(price.tax_rate),
            float(price.amount),
            float(price.amount * (price.tax_rate / 100)),
        )

    invoice_number = generate_invoice_number(
        device.premise.furs_id, device.device_id, seq_id
    )

    try:
        eor = company_api.api.get_invoice_eor(
            zoi=zoi,
            tax_number=company.tax_id,
            issued_date=invoice.issued_at,
            invoice_number=invoice_number,
            business_premise_id=device.premise.furs_id,
            electronic_device_id=device.device_id,
            invoice_amount=float(total_invoice_amount),
            taxes_per_seller=[seller_one],
            operator_tax_number=invoice.operator_tax_id,
            subsequent_submit=subsequent_submit,
        )
    except Exception as e:
        logger.warning("Failed to get EOR for invoice", exc_info=e)
        raise HTTPException(status_code=502, detail=str(e))

    created_invoice = invoices.create(
        db,
        schemas.InvoiceCreate(
            zoi=zoi,
            eor=eor,
            invoice_number=invoice_number,
            total=total_invoice_amount,
            user_id=user.id,
            company_id=user.company_id,
            device_id=device.id,
            issued_at=invoice.issued_at,
        ),
    )

    return InvoiceResponse(
        invoice_number=invoice_number,
        internal_id=created_invoice.id,
        zoi=zoi,
        eor=eor,
        issued_at=invoice.issued_at,
    )


@router.get(
    "/get/{invoice_id}",
    summary="Get an invoice by ID",
    status_code=200,
    response_model=schemas.Invoice,
)
async def get_invoice(
    invoice_id: int,
    user: models.User = Depends(
        ActiveUserWithRole([models.UserRole.ORGANIZATION_ADMIN, models.UserRole.ADMIN])
    ),
    db: Session = Depends(get_db),
):
    invoice = invoices.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    elif invoice.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="Invoice not owned by company")

    return invoice


@router.get(
    "/list",
    summary="List invoices",
    status_code=200,
    response_model=List[schemas.Invoice],
)
async def list_invoices(
    user: models.User = Depends(
        ActiveUserWithRole([models.UserRole.ORGANIZATION_ADMIN, models.UserRole.ADMIN])
    ),
    db: Session = Depends(get_db),
):
    return invoices.get_by_company_id(db, user.company_id)


@router.get(
    "/list/all",
    summary="List all invoices",
    status_code=200,
    response_model=List[schemas.Invoice],
)
async def list_all_invoices(
    _: models.User = Depends(ActiveUserWithRole([models.UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    return invoices.get_all(db)
