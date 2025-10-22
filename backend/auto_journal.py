from __future__ import annotations

import json
from datetime import date as _date
from typing import Any, Dict

from utils.llm_client import LLMClient

from .db_manager import get_session_for_client
from .models_journal import CorrectionHistory, JournalEntry
from . import llm_trainer
from .settings import settings


def _llm() -> LLMClient:
    return LLMClient(base_url=settings.llm_base_url, model=settings.llm_model, api_key=settings.llm_api_key)


def classify_with_llm(summary: str, amount: float, date: str, client_code: str) -> Dict[str, Any]:
    examples = llm_trainer.generate_client_examples(client_code)
    prompt = f"""
    あなたは日本の会計AIです。
    以下の取引を基に勘定科目を推定してください。

    取引情報:
    日付: {date}
    摘要: {summary}
    金額: {amount}

    過去の傾向:
    {examples}

    出力形式: JSON (strict JSON)
    {{
      "debit_account": "...",
      "credit_account": "...",
      "confidence": 0.0,
      "reason": "..."
    }}
    """
    content = _llm().chat(
        messages=[{"role": "user", "content": prompt}],
        response_format="json",
        temperature=0.0,
    )
    try:
        return json.loads(content)
    except Exception:
        return {"debit_account": None, "credit_account": None, "confidence": 0.0, "reason": ""}


def record_correction(client_code: str, entry_id: int, new_debit: str, new_credit: str, reason: str, reviewer: str) -> None:
    db = get_session_for_client(client_code)
    try:
        entry = db.query(JournalEntry).get(entry_id)
        if not entry:
            return
        correction = CorrectionHistory(
            entry_id=entry.id,
            old_debit=entry.debit_account,
            old_credit=entry.credit_account,
            new_debit=new_debit,
            new_credit=new_credit,
            reason=reason,
            reviewer=reviewer,
        )
        entry.reviewed = True
        entry.debit_account = new_debit
        entry.credit_account = new_credit
        db.add(correction)
        db.commit()
        llm_trainer.update_examples_with_correction(client_code, correction)
    finally:
        db.close()

