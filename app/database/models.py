import enum

from app.database import Base
from furs_fiscal.api import (
    TYPE_MOVABLE_PREMISE_A,
    TYPE_MOVABLE_PREMISE_B,
    TYPE_MOVABLE_PREMISE_C,
)
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class BusinessPremiseType(enum.Enum):
    MOVABLE = "MOVABLE"
    IMMOVABLE = "IMMOVABLE"


class MovablePremiseType(enum.Enum):
    A = TYPE_MOVABLE_PREMISE_A
    B = TYPE_MOVABLE_PREMISE_B
    C = TYPE_MOVABLE_PREMISE_C


class UserRole(enum.IntEnum):
    DEFAULT = 0
    ORGANIZATION_ADMIN = 1
    ADMIN = 2


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    tax_id = Column(BigInteger, unique=True, nullable=False)
    cert_key = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    users = relationship("User", back_populates="company")
    premises = relationship("BusinessPremise", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.DEFAULT)
    active = Column(Boolean, nullable=False, server_default="1")

    company_id = Column(ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="users")

    invoices = relationship("Invoice", back_populates="user")


class BusinessPremise(Base):
    __tablename__ = "business_premises"
    id = Column(Integer, primary_key=True, index=True)
    furs_id = Column(String, nullable=False)
    validity_from = Column(DateTime, nullable=False, server_default=func.now())
    notes = Column(String, nullable=True)
    premise_type = Column(Enum(BusinessPremiseType), nullable=False)

    # Movable premise-specific info
    movable_type = Column(Enum(MovablePremiseType))

    # Immovable premise-specific info
    real_estate_cadastral_number = Column(Integer)
    real_estate_building_number = Column(Integer)
    real_estate_building_section_number = Column(Integer)
    street = Column(String)
    house_number = Column(String)
    house_number_additional = Column(String)
    community = Column(String)
    city = Column(String)
    postal_code = Column(String)

    company_id = Column(ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="premises")

    devices = relationship("Device", back_populates="premise")


class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, nullable=False)
    seq_invoice_id = Column(Integer, nullable=False, server_default="0")
    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    premise_id = Column(ForeignKey("business_premises.id"), nullable=False)
    premise: BusinessPremise = relationship("BusinessPremise", back_populates="devices")

    invoices = relationship("Invoice", back_populates="device")


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    zoi = Column(String, nullable=False)
    eor = Column(String, nullable=False)
    invoice_number = Column(String, nullable=False)
    issued_at = Column(DateTime, nullable=False)
    total = Column(Float(asdecimal=True), nullable=False)

    user_id = Column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="invoices")

    company_id = Column(ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="invoices")

    device_id = Column(ForeignKey("devices.id"), nullable=False)
    device = relationship("Device", back_populates="invoices")
