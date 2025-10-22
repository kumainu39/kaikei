"""Database session and engine management."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.settings import settings
from backend.models import Client

DATABASE_URL = settings.database_url

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def session_scope() -> Generator:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_client_by_key(api_key: str) -> Optional[Client]:
    with SessionLocal() as session:
        return session.query(Client).filter(Client.api_key == api_key).first()


def get_client_by_code(session, code: str) -> Optional[Client]:
    return session.query(Client).filter(Client.code == code).first()
