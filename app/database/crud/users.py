from typing import List, Optional

from app.database import models, schemas
from argon2 import PasswordHasher
from sqlalchemy.orm import Session


def get_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_all(db: Session) -> List[models.User]:
    return db.query(models.User).all()


def get_by_company_id(db: Session, company_id: int) -> List[models.User]:
    return db.query(models.User).filter(models.User.company_id == company_id).all()


def create(db: Session, user: schemas.UserCreate) -> models.User:
    hash = PasswordHasher().hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hash,
        role=user.role,
        company_id=user.company_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
