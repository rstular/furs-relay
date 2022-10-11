from app import certificates
from app.database.models import UserRole
from app.database.schemas import User
from app.util.auth import ActiveUserWithRole
from app.util.datatypes import ActionResponse
from fastapi import APIRouter, Depends
from loguru import logger

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.post(
    "/refresh", summary="Reload all certificates", response_model=ActionResponse
)
async def refresh_certificates(_: User = Depends(ActiveUserWithRole([UserRole.ADMIN]))):
    logger.info("Certificate reload requested")
    certificates.load()
    return ActionResponse(success=True)
