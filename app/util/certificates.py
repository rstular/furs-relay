import json
from base64 import b64decode
from dataclasses import dataclass
from typing import List

from app.database import SessionLocal
from app.database.crud import companies
from app.database.models import Company
from app.settings import (
    CERTIFICATE_DIR,
    CERTIFICATE_KEY,
    FURS_API_PRODUCTION,
    FURS_API_TIMEOUT,
)
from Crypto.Cipher import ChaCha20_Poly1305
from fastapi import HTTPException
from furs_fiscal.api import FURSBusinessPremiseAPI, FURSInvoiceAPI
from loguru import logger

loaded_certificates = {}


@dataclass
class CompanyAPI:
    tax_id: int
    api: FURSInvoiceAPI
    premise_api: FURSBusinessPremiseAPI


def get_apis() -> dict[int, CompanyAPI]:
    return loaded_certificates


def get_api_for_company(company_id: int) -> CompanyAPI:
    try:
        return loaded_certificates[company_id]
    except:
        raise HTTPException(status_code=404, detail="Company not found")


def load():
    logger.debug("Loading certificates")
    with SessionLocal() as db:
        active_companies = companies.get_all_active(db)
    load_for_companies(active_companies)


def load_for_companies(companies: List[Company]):
    for company in companies:
        cert_path = CERTIFICATE_DIR / f"{company.tax_id}.p12"
        if not cert_path.is_file():
            logger.warning(f"Certificate for company {company.tax_id} not found")
            continue

        try:
            cert_password = decrypt_cert_key(company.cert_key)
        except Exception as e:
            logger.error(
                f"Failed to decrypt certificate key for company {company.tax_id}: {e}"
            )
            continue

        if cert_password is None or len(cert_password) == 0:
            continue

        # TODO: maybe load certificates from byte buffers?
        loaded_certificates[company.id] = CompanyAPI(
            company.tax_id,
            FURSInvoiceAPI(
                p12_path=cert_path,
                p12_password=cert_password,
                production=FURS_API_PRODUCTION,
                request_timeout=float(FURS_API_TIMEOUT),
            ),
            FURSBusinessPremiseAPI(
                p12_path=cert_path,
                p12_password=cert_password,
                production=FURS_API_PRODUCTION,
                request_timeout=float(FURS_API_TIMEOUT),
            ),
        )
        logger.debug(f"Loaded certificate for company {company.tax_id}")
    logger.info(f"Loaded {len(loaded_certificates)} certificate(s)")


def decrypt_cert_key(cert_key_data: str) -> str:
    key = CERTIFICATE_KEY
    cert_key_data = json.loads(cert_key_data)
    jk = ["nonce", "ciphertext", "tag"]
    jv = {k: b64decode(cert_key_data[k]) for k in jk}

    cipher = ChaCha20_Poly1305.new(key=key, nonce=jv["nonce"])
    plaintext = cipher.decrypt_and_verify(jv["ciphertext"], jv["tag"])
    return plaintext.decode("utf-8")
