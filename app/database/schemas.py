from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from app.database.models import BusinessPremiseType, MovablePremiseType
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str
    role: int
    company_id: int


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    active: bool

    class Config:
        orm_mode = True


class UserInDb(User):
    password: str


class DeviceBase(BaseModel):
    device_id: str
    premise_id: int
    is_active: bool = True


class DeviceCreate(DeviceBase):
    seq_invoice_id: Optional[int]
    created_at: Optional[datetime]


class Device(DeviceBase):
    id: int
    seq_invoice_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class BusinessPremiseBase(BaseModel):
    furs_id: str
    premise_type: BusinessPremiseType
    company_id: int
    validity_from: Optional[datetime] = None
    notes: Optional[str] = None
    movable_type: Optional[MovablePremiseType] = None
    real_estate_cadastral_number: Optional[int] = None
    real_estate_building_number: Optional[int] = None
    real_estate_building_section_number: Optional[int] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    house_number_additional: Optional[str] = None
    community: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None


class CreateBusinessPremise(BusinessPremiseBase):
    pass


class BusinessPremise(BusinessPremiseBase):
    id: int
    devices: List[Device] = []

    class Config:
        orm_mode = True


class CompanyBase(BaseModel):
    name: str
    tax_id: int
    is_active: bool = True


class CompanyCreate(CompanyBase):
    cert_key: str


class Company(CompanyBase):
    id: int
    users: List[User] = []
    devices: List[Device] = []

    class Config:
        orm_mode = True


class CompanyInDb(Company):
    cert_key: str


class InvoiceBase(BaseModel):
    zoi: str
    eor: str
    invoice_number: str
    issued_at: datetime
    total: Decimal
    user_id: int
    company_id: int
    device_id: int


class InvoiceCreate(InvoiceBase):
    pass


class Invoice(InvoiceBase):
    id: int

    class Config:
        orm_mode = True
