"""ORM models for client risk profiling."""
from __future__ import annotations
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RiskProfile(Base):
    __tablename__ = "risk_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String, ForeignKey("clients.id"), nullable=False
    )
    advisor_id: Mapped[str] = mapped_column(
        String, ForeignKey("advisors.id"), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_category: Mapped[str] = mapped_column(String, nullable=False)
    question_responses: Mapped[str | None] = mapped_column(Text, nullable=True)
    advisor_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    compliance_pdf_path: Mapped[str | None] = mapped_column(String, nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    retention_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
