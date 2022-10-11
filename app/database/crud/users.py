from typing import Optional

from app.database import models, schemas
from argon2 import PasswordHasher
from sqlalchemy.orm import Session


def get_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


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
