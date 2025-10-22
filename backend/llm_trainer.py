from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from .models_journal import CorrectionHistory


def _examples_path(client_code: str) -> Path:
    p = Path("clients")
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{client_code}_examples.json"


def generate_client_examples(client_code: str) -> str:
    path = _examples_path(client_code)
    if not path.exists():
        return "[]"
    return path.read_text(encoding="utf-8")


def update_examples_with_correction(client_code: str, correction: CorrectionHistory) -> None:
    path = _examples_path(client_code)
    examples: List[dict[str, Any]] = []
    if path.exists():
        try:
            examples = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            examples = []
    examples.insert(0, {
        "summary": correction.entry.summary if correction.entry else "",
        "corrected_to": [correction.new_debit, correction.new_credit],
        "reviewer_reason": correction.reason,
    })
    path.write_text(json.dumps(examples[:50], ensure_ascii=False, indent=2), encoding="utf-8")

