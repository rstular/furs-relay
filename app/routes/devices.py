from typing import List

from app.database import get_db
from app.database.crud import devices
from app.database.models import UserRole
from app.database.schemas import Device, User
from app.util.auth import ActiveUserWithRole, get_current_active_user
from app.util.datatypes import ActionResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get(
    "/list",
    summary="Get a list of all devices for your company",
    response_model=List[Device],
)
async def get_devices(
    user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    return devices.get_all_for_company(db, user.company_id)


@router.get(
    "/list/all", summary="Get a list of all devices", response_model=List[Device]
)
async def get_all_devices(
    _: User = Depends(ActiveUserWithRole([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    return devices.get_all(db)


@router.post(
    "/disable/{device_id}",
    summary="Disable a device",
    response_model=ActionResponse,
)
async def disable_device(
    device_id: int,
    user: User = Depends(
        ActiveUserWithRole([UserRole.ADMIN, UserRole.ORGANIZATION_ADMIN])
    ),
    db: Session = Depends(get_db),
):
    if user.role < int(UserRole.ADMIN):
        device_data = devices.get(db, device_id)
        if device_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with id {device_id} not found",
            )
        elif device_data.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permission to edit foreign device",
            )
    if devices.set_active(db, device_id, False) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found",
        )
    return ActionResponse(success=True)


@router.post(
    "/enable/{device_id}",
    summary="Enable a device",
    response_model=ActionResponse,
)
async def enable_device(
    device_id: int,
    user: User = Depends(
        ActiveUserWithRole([UserRole.ADMIN, UserRole.ORGANIZATION_ADMIN])
    ),
    db: Session = Depends(get_db),
):
    if user.role < int(UserRole.ADMIN):
        device_data = devices.get(db, device_id)
        if device_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with id {device_id} not found",
            )
        elif device_data.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permission to edit foreign device",
            )

    if devices.set_active(db, device_id, True) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found",
        )
    return ActionResponse(success=True)
