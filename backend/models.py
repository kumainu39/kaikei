"""SQLAlchemy models representing accounting entities."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)

    debit_journals = relationship(
        "Journal", foreign_keys="Journal.debit_account_id", back_populates="debit_account"
    )
    credit_journals = relationship(
        "Journal", foreign_keys="Journal.credit_account_id", back_populates="credit_account"
    )


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=date.today)
    debit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    credit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)
    tax_type = Column(String(20), nullable=True)

    debit_account = relationship("Account", foreign_keys=[debit_account_id], back_populates="debit_journals")
    credit_account = relationship("Account", foreign_keys=[credit_account_id], back_populates="credit_journals")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(100), nullable=False)
    debit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    credit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)

    debit_account = relationship("Account", foreign_keys=[debit_account_id])
    credit_account = relationship("Account", foreign_keys=[credit_account_id])
