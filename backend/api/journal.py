from __future__ import annotations

from datetime import date
from typing import Any, List

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from ..auto_journal import record_correction
from ..db_manager import get_client_by_key, get_session_for_client
from ..models_journal import JournalEntry


router = APIRouter(prefix="/api/journal", tags=["journal"])


class JournalCreate(BaseModel):
    date: date
    summary: str
    amount: float
    debit_account: str
    credit_account: str


class JournalRead(BaseModel):
    id: int
    date: date
    summary: str
    amount: float
    debit_account: str
    credit_account: str
    confidence: float | None = None
    ai_reason: str | None = None
    reviewed: bool
    pdf_path: str | None = None


@router.get("/", response_model=List[JournalRead])
def list_entries(x_client_key: str = Header(...)):
    client = get_client_by_key(x_client_key)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client key")
    db = get_session_for_client(client.code)
    try:
        rows = db.query(JournalEntry).order_by(JournalEntry.id.desc()).all()
        return [
            JournalRead(
                id=r.id,
                date=r.date,
                summary=r.summary,
                amount=r.amount,
                debit_account=r.debit_account,
                credit_account=r.credit_account,
                confidence=r.confidence,
                ai_reason=r.ai_reason,
                reviewed=bool(r.reviewed),
                pdf_path=r.pdf_path,
            )
            for r in rows
        ]
    finally:
        db.close()


@router.post("/", response_model=JournalRead)
def create_entry(payload: JournalCreate, x_client_key: str = Header(...)):
    client = get_client_by_key(x_client_key)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client key")
    db = get_session_for_client(client.code)
    try:
        r = JournalEntry(
            date=payload.date,
            summary=payload.summary,
            amount=payload.amount,
            debit_account=payload.debit_account,
            credit_account=payload.credit_account,
            reviewed=False,
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        return JournalRead(
            id=r.id,
            date=r.date,
            summary=r.summary,
            amount=r.amount,
            debit_account=r.debit_account,
            credit_account=r.credit_account,
            confidence=r.confidence,
            ai_reason=r.ai_reason,
            reviewed=bool(r.reviewed),
            pdf_path=r.pdf_path,
        )
    finally:
        db.close()


class CorrectionPayload(BaseModel):
    entry_id: int
    new_debit: str
    new_credit: str
    reason: str


@router.post("/correct")
def correct_entry(payload: CorrectionPayload, x_client_key: str = Header(...)):
    client = get_client_by_key(x_client_key)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client key")
    record_correction(client.code, payload.entry_id, payload.new_debit, payload.new_credit, payload.reason, reviewer="user")
    return {"status": "corrected"}

