from pathlib import Path

from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=1440
)
JWT_KEY = config("JWT_KEY", cast=str)
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")

CERTIFICATE_DIR = Path(
    config("CERTIFICATE_DIR", cast=str, default="./data/certificates")
)
CERTIFICATE_KEY = bytes.fromhex(config("CERTIFICATE_KEY", cast=str))
FURS_API_TIMEOUT = config("FURS_API_TIMEOUT", cast=int, default=10)
FURS_API_PRODUCTION = config("FURS_API_PRODUCTION", cast=bool, default=False)

SOFTWARE_SUPPLIER_TAX_NUMBER = config("SOFTWARE_SUPPLIER_TAX_NUMBER", cast=int)
