"""FastAPI application exposing accounting endpoints."""
from __future__ import annotations

from datetime import date
from typing import Any, Generator

from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.auto_journal import suggest_accounts
from backend.db import SessionLocal, engine, get_client_by_key
from backend.models import Account, Journal, Client
from utils.logging_config import setup_logging
from utils.scheduler import shutdown_scheduler, start_scheduler
from utils.settings import settings
from .ai_classifier import get_classifier
from .bank_connector import fetch_bank_transactions
from .card_connector import fetch_card_transactions
from .scan_import import router as scan_router

setup_logging()

app = FastAPI(title="Kaikei Accounting API", version="0.1.0")
app.include_router(scan_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AccountCreate(BaseModel):
    code: str
    name: str
    type: str


class AccountRead(AccountCreate):
    id: int

    class Config:
        orm_mode = True


class JournalBase(BaseModel):
    date: date = Field(default_factory=date.today)
    debit_account_id: int
    credit_account_id: int
    amount: float = Field(gt=0)
    summary: str | None = None
    tax_type: str | None = None


class JournalCreate(JournalBase):
    pass


class JournalRead(JournalBase):
    id: int

    class Config:
        orm_mode = True


class JournalSuggestionRequest(BaseModel):
    summary: str
    amount: float


class AutoJournalResponse(BaseModel):
    debit: int | None = None
    credit: int | None = None


class ImportResponse(BaseModel):
    imported: list[dict[str, Any]]


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_client(x_client_key: str | None = Header(default=None)) -> Client:
    if not x_client_key:
        raise HTTPException(status_code=401, detail="X-Client-Key required")
    client = get_client_by_key(x_client_key)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client key")
    return client


@app.on_event("startup")
def on_startup() -> None:
    models.Base.metadata.create_all(bind=engine)
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    shutdown_scheduler()


@app.get("/api/accounts", response_model=list[AccountRead])
def list_accounts(db: Session = Depends(get_db)) -> list[AccountRead]:
    return db.query(Account).order_by(Account.code).all()


@app.post("/api/accounts", response_model=AccountRead, status_code=201)
def create_account(account: AccountCreate, db: Session = Depends(get_db)) -> AccountRead:
    existing = db.query(Account).filter_by(code=account.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists")
    account_obj = Account(**account.dict())
    db.add(account_obj)
    db.commit()
    db.refresh(account_obj)
    return account_obj


@app.get("/api/journal", response_model=list[JournalRead])
def list_journals(db: Session = Depends(get_db), client: Client = Depends(get_client)) -> list[JournalRead]:
    return (
        db.query(Journal)
        .filter(Journal.client_id == client.id)
        .order_by(Journal.date.desc())
        .all()
    )


@app.post("/api/journal", response_model=JournalRead, status_code=201)
def create_journal(entry: JournalCreate, db: Session = Depends(get_db), client: Client = Depends(get_client)) -> JournalRead:
    journal = Journal(**entry.dict(), client_id=client.id)
    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal


@app.delete("/api/journal/{journal_id}", status_code=204)
def delete_journal(journal_id: int, db: Session = Depends(get_db), client: Client = Depends(get_client)) -> None:
    journal = db.get(Journal, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    if journal.client_id != client.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(journal)
    db.commit()


@app.post("/api/import/bank", response_model=ImportResponse)
def import_bank_transactions(db: Session = Depends(get_db)) -> ImportResponse:
    transactions = fetch_bank_transactions(settings.bank_api_key)
    imported_entries: list[dict[str, Any]] = []
    for transaction in transactions:
        debit, credit = suggest_accounts(db, transaction["summary"])
        imported_entries.append(
            {
                "date": transaction["date"],
                "summary": transaction["summary"],
                "amount": transaction["amount"],
                "debit_account": debit.name if debit else None,
                "credit_account": credit.name if credit else None,
            }
        )
    return ImportResponse(imported=imported_entries)


@app.post("/api/import/card", response_model=ImportResponse)
def import_card_transactions(db: Session = Depends(get_db)) -> ImportResponse:
    transactions = fetch_card_transactions(settings.card_api_key)
    imported_entries: list[dict[str, Any]] = []
    for transaction in transactions:
        debit, credit = suggest_accounts(db, transaction["summary"])
        imported_entries.append(
            {
                "date": transaction["date"],
                "summary": transaction["summary"],
                "amount": transaction["amount"],
                "debit_account": debit.name if debit else None,
                "credit_account": credit.name if credit else None,
            }
        )
    return ImportResponse(imported=imported_entries)


@app.post("/api/auto_journal", response_model=AutoJournalResponse)
async def auto_journal(entry: JournalSuggestionRequest, db: Session = Depends(get_db), client: Client = Depends(get_client)) -> AutoJournalResponse:
    if settings.ai_mode == "llm":
        from backend.auto_journal import suggest_accounts_llm_rich
        # Use rich to leverage client-scoped few-shot, then map names back to IDs
        result = suggest_accounts_llm_rich(db, entry.summary, entry.amount, date.today().isoformat(), client_id=client.id)
        debit = db.query(Account).filter(Account.name == result.get("debit_account")).first() if result.get("debit_account") else None
        credit = db.query(Account).filter(Account.name == result.get("credit_account")).first() if result.get("credit_account") else None
        return AutoJournalResponse(
            debit=debit.id if debit else None,
            credit=credit.id if credit else None,
        )
    # Fallback to local ML model
    classifier = get_classifier()
    result = classifier.predict(entry.summary, entry.amount)
    # Assume the classifier returns account IDs if available
    return AutoJournalResponse(debit=result.get("debit"), credit=result.get("credit"))
