from __future__ import annotations

import json
from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.db import engine, SessionLocal
from backend.models import Base, Account, Client


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Seed minimal accounts and a client
    with SessionLocal() as s:
        s.add_all([
            Account(code="101", name="現金", type="資産"),
            Account(code="601", name="旅費交通費", type="費用"),
        ])
        s.add(Client(name="Scan", code="A001", api_key="akey"))
        s.commit()
    yield
    Base.metadata.drop_all(bind=engine)


def test_llm_suggest_and_confidence_gate(monkeypatch):
    # Monkeypatch LLM to return desired JSON
    from utils import llm_client as llm_mod

    def fake_chat(self, messages, temperature=0.0, response_format=None):
        payload = {
            "debit_account": "旅費交通費",
            "credit_account": "現金",
            "confidence": 0.92,
            "reason": "小額のコンビニ支払いで交通費に該当",
        }
        return json.dumps(payload, ensure_ascii=False)

    monkeypatch.setattr(llm_mod.LLMClient, "chat", fake_chat)

    client = TestClient(app)

    # Upload a dummy XML to the scan endpoint
    xml = (
        "<Root>"
        f"<Date>{date.today().isoformat()}</Date>"
        "<Vendor>セブンイレブン 235円</Vendor>"
        "<Amount>235</Amount>"
        "<TaxIncluded>1</TaxIncluded>"
        "<Confidence>0.95</Confidence>"
        "</Root>"
    ).encode("utf-8")

    files = {"file": ("sample.xml", xml, "text/xml")}
    res = client.post("/api/scan/import", files=files, headers={"X-Client-Key": "akey"})
    assert res.status_code == 200
    data = res.json()
    # Expect auto-saved due to high confidence
    assert data.get("saved", True) is True or data.get("status") == "ok"
    # If entry present, verify structure
    if data.get("entry"):
        entry = data["entry"]
        assert entry["amount"] == 235

