from typing import List

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


@router.get(
    "/list", summary="Get a list of all loaded certificates", response_model=List[str]
)
async def get_certificates(
    _: User = Depends(ActiveUserWithRole([UserRole.ADMIN])),
):
    company_taxid_list = []
    for api_data in certificates.get_apis().values():
        company_taxid_list.append(api_data.tax_id)
    return company_taxid_list
