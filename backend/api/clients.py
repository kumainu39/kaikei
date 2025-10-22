from __future__ import annotations

import secrets
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db_manager import get_master_session
from ..models_client import Client


router = APIRouter(prefix="/api/clients", tags=["clients"])


class ClientCreate(BaseModel):
    name: str
    code: str
    base_folder: str | None = None


class ClientRead(BaseModel):
    id: int
    name: str
    code: str
    base_folder: str | None
    api_key: str | None


@router.post("/", response_model=ClientRead)
def create_client(payload: ClientCreate):
    with get_master_session() as s:
        existing = s.query(Client).filter(Client.code == payload.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="Client code exists")
        api_key = secrets.token_urlsafe(24)
        c = Client(name=payload.name, code=payload.code, base_folder=payload.base_folder, api_key=api_key)
        s.add(c)
        s.commit()
        s.refresh(c)
        return ClientRead(id=c.id, name=c.name, code=c.code, base_folder=c.base_folder, api_key=c.api_key)


@router.get("/", response_model=List[ClientRead])
def list_clients():
    with get_master_session() as s:
        rows = s.query(Client).order_by(Client.code).all()
        return [ClientRead(id=c.id, name=c.name, code=c.code, base_folder=c.base_folder, api_key=c.api_key) for c in rows]


@router.delete("/{client_code}")
def delete_client(client_code: str):
    with get_master_session() as s:
        c = s.query(Client).filter(Client.code == client_code).first()
        if not c:
            raise HTTPException(status_code=404, detail="Client not found")
        s.delete(c)
        s.commit()
        return {"status": "deleted"}

