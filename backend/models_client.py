from __future__ import annotations

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .models_base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    base_folder = Column(String, nullable=True)  # ScanSnap folder
    api_key = Column(String, unique=True, nullable=True)

    # For parity with earlier spec; target models live per-client DB, so this is registry only
    # journal_entries = relationship("JournalEntry", back_populates="client")

