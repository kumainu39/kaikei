from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.clients import router as clients_router
from .api.journal import router as journal_router
from .api.scan_import import router as scan_router
from .scheduler import start_scheduler, shutdown_scheduler


app = FastAPI(title="Kaikei Accounting API (Multi-tenant)", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients_router)
app.include_router(journal_router)
app.include_router(scan_router)


@app.on_event("startup")
def _startup():
    start_scheduler()


@app.on_event("shutdown")
def _shutdown():
    shutdown_scheduler()

