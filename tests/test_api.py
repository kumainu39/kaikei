from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.db import engine
from backend.models import Base


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_account_and_journal():
    client = TestClient(app)

    account_payload = {"code": "101", "name": "現金", "type": "資産"}
    response = client.post("/api/accounts", json=account_payload)
    assert response.status_code == 201
    account_id = response.json()["id"]

    other_account_payload = {"code": "201", "name": "売上", "type": "収益"}
    response = client.post("/api/accounts", json=other_account_payload)
    assert response.status_code == 201
    other_account_id = response.json()["id"]

    journal_payload = {
        "date": "2024-01-01",
        "debit_account_id": account_id,
        "credit_account_id": other_account_id,
        "amount": 1000,
        "summary": "売上計上",
        "tax_type": "対象外",
    }
    journal_response = client.post("/api/journal", json=journal_payload)
    assert journal_response.status_code == 201
    data = journal_response.json()
    assert data["amount"] == 1000
    assert data["summary"] == "売上計上"


def test_auto_journal_stub():
    client = TestClient(app)
    response = client.post("/api/auto_journal", json={"summary": "テスト", "amount": 100})
    assert response.status_code == 200
    payload = response.json()
    assert "debit" in payload and "credit" in payload
