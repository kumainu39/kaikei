"""Placeholder for bank API integration."""
from __future__ import annotations

from typing import Any


def fetch_bank_transactions(api_key: str | None) -> list[dict[str, Any]]:
    """Return a list of fake bank transactions until real integration is implemented."""
    if not api_key:
        return []
    return [
        {"date": "2024-01-01", "summary": "ATM Deposit", "amount": 50000.0},
        {"date": "2024-01-02", "summary": "Utility Payment", "amount": -8000.0},
    ]
