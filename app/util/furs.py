from typing import List

from app.database import SessionLocal, models
from app.database.crud import companies, premises
from app.settings import SOFTWARE_SUPPLIER_TAX_NUMBER
from loguru import logger

from .certificates import get_api_for_company


def register_premises():
    logger.debug("Registering premises")
    with SessionLocal() as db:
        active_companies = companies.get_all_active(db)
    for company in active_companies:
        premises_to_register: List[
            models.BusinessPremise
        ] = premises.get_all_for_company(db, company.id)
        for premise in premises_to_register:
            if premise.premise_type == models.BusinessPremiseType.MOVABLE:
                try:
                    register_movable_premise(premise)
                except Exception as e:
                    logger.error(
                        f"Failed to register movable premise {premise.furs_id} for company {company.tax_id}: {e}"
                    )
            elif premise.premise_type == models.BusinessPremiseType.IMMOVABLE:
                try:
                    register_immovable_premise(premise)
                except Exception as e:
                    logger.error(
                        f"Failed to register immovable premise {premise.furs_id} for company {company.tax_id}: {e}"
                    )
            else:
                logger.warning(f"Unknown premise type: {premise.premise_type}")
    logger.info("Registered premises")


def register_movable_premise(premise: models.BusinessPremise):
    company_api = get_api_for_company(premise.company_id)
    if not company_api.premise_api.register_movable_business_premise(
        tax_number=company_api.tax_id,
        premise_id=premise.furs_id,
        movable_type=premise.movable_type.value,
        validity_date=premise.validity_from,
        software_supplier_tax_number=SOFTWARE_SUPPLIER_TAX_NUMBER,
        foreign_software_supplier_name=None,
        special_notes=premise.notes or "None",
    ):
        raise Exception("Failed to register premise")


def register_immovable_premise(_premise: models.BusinessPremise):
    raise NotImplementedError("Immovable premises are not implemented yet")
