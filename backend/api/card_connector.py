"""Placeholder for credit card API integration."""
from __future__ import annotations

from typing import Any


def fetch_card_transactions(api_key: str | None) -> list[dict[str, Any]]:
    if not api_key:
        return []
    return [
        {"date": "2024-01-03", "summary": "Online Purchase", "amount": -12000.0},
        {"date": "2024-01-05", "summary": "Subscription", "amount": -980.0},
    ]
