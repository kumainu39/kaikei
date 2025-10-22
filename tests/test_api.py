from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.db import engine, SessionLocal
from backend.models import Base, Client


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_account_and_journal():
    client = TestClient(app)

    # seed client for auth
    with SessionLocal() as s:
        c = Client(name="Test", code="T001", api_key="testkey")
        s.add(c)
        s.commit()

    # create accounts
    response = client.post("/api/accounts", json={"code": "101", "name": "現金", "type": "資産"})
    assert response.status_code == 201
    account_id = response.json()["id"]

    response = client.post("/api/accounts", json={"code": "201", "name": "売上", "type": "収益"})
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
    journal_response = client.post("/api/journal", json=journal_payload, headers={"X-Client-Key": "testkey"})
    assert journal_response.status_code == 201
    data = journal_response.json()
    assert data["amount"] == 1000
    assert data["summary"] == "売上計上"


def test_auto_journal_stub():
    client = TestClient(app)
    with SessionLocal() as s:
        c = Client(name="Test2", code="T002", api_key="testkey2")
        s.add(c)
        s.commit()
    response = client.post(
        "/api/auto_journal",
        json={"summary": "テスト", "amount": 100},
        headers={"X-Client-Key": "testkey2"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "debit" in payload and "credit" in payload

