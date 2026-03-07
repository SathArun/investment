"""ORM models for clients and investment goals."""
from __future__ import annotations
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    advisor_id: Mapped[str] = mapped_column(
        String, ForeignKey("advisors.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tax_bracket: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_category: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    goals: Mapped[list["Goal"]] = relationship("Goal", back_populates="client")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String, ForeignKey("clients.id"), nullable=False
    )
    advisor_id: Mapped[str] = mapped_column(
        String, ForeignKey("advisors.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    target_amount_inr: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    current_corpus_inr: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_sip_inr: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_stepup_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    inflation_rate: Mapped[float | None] = mapped_column(
        Float, default=0.06, nullable=True
    )
    expected_return_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )

    client: Mapped["Client"] = relationship("Client", back_populates="goals")
