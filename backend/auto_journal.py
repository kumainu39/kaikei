"""Automatic journal suggestion logic."""
from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from backend.models import Account, Rule


def match_rule(summary: str, rules: Iterable[Rule]) -> Rule | None:
    if not summary:
        return None
    summary_lower = summary.lower()
    for rule in rules:
        if rule.keyword.lower() in summary_lower:
            return rule
    return None


def suggest_accounts(session: Session, summary: str) -> tuple[Account | None, Account | None]:
    rules = session.query(Rule).all()
    rule = match_rule(summary, rules)
    if rule:
        return rule.debit_account, rule.credit_account
    return None, None
