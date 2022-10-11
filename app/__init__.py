from fastapi import FastAPI

from .database import engine, models
from .routes import (
    AuthRouter,
    CompaniesRouter,
    DevicesRouter,
    InvoicesRouter,
    PremisesRouter,
)
from .util import certificates, furs
from .util.logging import initialize as initialize_logging

initialize_logging()
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Davcna blagajna API")
app.include_router(AuthRouter)
app.include_router(CompaniesRouter)
app.include_router(InvoicesRouter)
app.include_router(DevicesRouter)
app.include_router(PremisesRouter)


@app.on_event("startup")
async def startup():
    certificates.load()
    furs.register_premises()
