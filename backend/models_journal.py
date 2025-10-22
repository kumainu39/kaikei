from __future__ import annotations

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .models_base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    summary = Column(String)
    amount = Column(Float)
    debit_account = Column(String)
    credit_account = Column(String)
    confidence = Column(Float)
    ai_reason = Column(Text)
    reviewed = Column(Boolean, default=False)
    client_id = Column(Integer)
    pdf_path = Column(String)  # ScanSnap OCR source path

    corrections = relationship("CorrectionHistory", back_populates="entry")


class CorrectionHistory(Base):
    __tablename__ = "correction_history"

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    old_debit = Column(String)
    old_credit = Column(String)
    new_debit = Column(String)
    new_credit = Column(String)
    reason = Column(Text)
    reviewer = Column(String)

    entry = relationship("JournalEntry", back_populates="corrections")

