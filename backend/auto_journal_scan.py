from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date as _date
from pathlib import Path
from typing import Any, Dict

from .auto_journal import classify_with_llm
from .db_manager import get_session_for_client
from .models_journal import JournalEntry
from .settings import settings


def _parse_scansnap_xml(file_path: Path) -> dict[str, Any]:
    tree = ET.parse(file_path)
    root = tree.getroot()
    data: Dict[str, Any] = {}
    data["date"] = (root.findtext("Date") or "").strip()
    data["vendor"] = (root.findtext("Vendor") or "").strip()
    try:
        data["amount"] = float((root.findtext("Amount") or "0").strip())
    except ValueError:
        data["amount"] = 0.0
    data["tax_included"] = (root.findtext("TaxIncluded") or "").strip().lower() in {"1", "true", "yes"}
    data["confidence"] = float((root.findtext("Confidence") or "1.0").strip() or 1.0)
    return data


def process_scansnap_xml(file_path: Path, client_code: str) -> dict[str, Any]:
    payload = _parse_scansnap_xml(file_path)
    summary = payload.get("vendor") or ""
    amount = float(payload.get("amount") or 0.0)
    date_str = payload.get("date") or _date.today().isoformat()

    result = classify_with_llm(summary=summary, amount=amount, date=date_str, client_code=client_code)
    debit = result.get("debit_account")
    credit = result.get("credit_account")
    confidence = float(result.get("confidence", 0.0) or 0.0)
    reason = result.get("reason") or ""

    threshold = settings.ai_autopost_threshold
    db = get_session_for_client(client_code)
    try:
        if confidence >= threshold and debit and credit:
            entry = JournalEntry(
                date=_date.fromisoformat(date_str.replace("/", "-")) if date_str else _date.today(),
                summary=summary,
                amount=amount,
                debit_account=debit,
                credit_account=credit,
                confidence=confidence,
                ai_reason=reason,
                reviewed=False,
                client_id=None,
                pdf_path=str(file_path),
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return {"saved": True, "entry": {
                "id": entry.id,
                "date": entry.date.isoformat(),
                "summary": entry.summary,
                "amount": entry.amount,
                "debit_account": entry.debit_account,
                "credit_account": entry.credit_account,
            }, "confidence": confidence, "reason": reason}
        else:
            return {
                "saved": False,
                "suggestion": {"debit_account": debit, "credit_account": credit, "confidence": confidence, "reason": reason},
            }
    finally:
        db.close()

