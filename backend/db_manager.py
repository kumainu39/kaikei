from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models_base import Base
from .models_client import Client
from .models_journal import JournalEntry, CorrectionHistory
from .settings import settings


_engine_cache: Dict[str, any] = {}


def _ensure_client_schema(engine) -> None:
    # Create tables for per-client DB
    Base.metadata.create_all(bind=engine)


def get_engine_for_client(client_code: str):
    db_path = Path(f"clients/{client_code}.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_path}"
    if url in _engine_cache:
        return _engine_cache[url]
    engine = create_engine(url, connect_args={"check_same_thread": False})
    _engine_cache[url] = engine
    _ensure_client_schema(engine)
    return engine


def get_session_for_client(client_code: str):
    engine = get_engine_for_client(client_code)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return Session()


_master_engine = None


def get_master_engine():
    global _master_engine
    if _master_engine is None:
        Path("data").mkdir(parents=True, exist_ok=True)
        _master_engine = create_engine(settings.master_database_url, connect_args={"check_same_thread": False} if settings.master_database_url.startswith("sqlite") else {})
        # Only Client model is in master
        from sqlalchemy.orm import declarative_base
        # Reuse Base; ensure table exists
        Client.metadata.create_all(bind=_master_engine)  # type: ignore[attr-defined]
    return _master_engine


def get_master_session():
    engine = get_master_engine()
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return Session()


def get_client_by_key(api_key: str) -> Optional[Client]:
    with get_master_session() as s:
        return s.query(Client).filter(Client.api_key == api_key).first()


def get_client_by_code(code: str) -> Optional[Client]:
    with get_master_session() as s:
        return s.query(Client).filter(Client.code == code).first()

