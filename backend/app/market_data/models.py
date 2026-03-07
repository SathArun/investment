"""ORM models for market data: asset classes, mutual funds, NAV history, index history."""
from __future__ import annotations
from datetime import date
from datetime import datetime

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AssetClass(Base):
    __tablename__ = "asset_classes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    sub_category: Mapped[str | None] = mapped_column(String, nullable=True)
    sebi_risk_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_source: Mapped[str | None] = mapped_column(String, nullable=True)
    min_investment_inr: Mapped[float | None] = mapped_column(Float, nullable=True)
    typical_exit_load_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lock_in_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expense_ratio_typical: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_crypto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    mutual_funds: Mapped[list["MutualFund"]] = relationship(
        "MutualFund", back_populates="asset_class"
    )


class MutualFund(Base):
    __tablename__ = "mutual_funds"

    scheme_code: Mapped[str] = mapped_column(String, primary_key=True)
    scheme_name: Mapped[str] = mapped_column(String, nullable=False)
    asset_class_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("asset_classes.id"), nullable=True
    )
    amfi_category: Mapped[str | None] = mapped_column(String, nullable=True)
    amc_name: Mapped[str | None] = mapped_column(String, nullable=True)
    direct_plan: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expense_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    fund_manager: Mapped[str | None] = mapped_column(String, nullable=True)
    aum_crore: Mapped[float | None] = mapped_column(Float, nullable=True)
    inception_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        String, nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    asset_class: Mapped["AssetClass | None"] = relationship(
        "AssetClass", back_populates="mutual_funds"
    )
    nav_history: Mapped[list["NavHistory"]] = relationship(
        "NavHistory", back_populates="mutual_fund"
    )


class NavHistory(Base):
    __tablename__ = "nav_history"

    scheme_code: Mapped[str] = mapped_column(
        String, ForeignKey("mutual_funds.scheme_code"), primary_key=True
    )
    nav_date: Mapped[date] = mapped_column(Date, primary_key=True, nullable=False)
    nav: Mapped[float] = mapped_column(Float, nullable=False)

    mutual_fund: Mapped["MutualFund"] = relationship(
        "MutualFund", back_populates="nav_history"
    )


class IndexHistory(Base):
    __tablename__ = "index_history"

    ticker: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    price_date: Mapped[date] = mapped_column(Date, primary_key=True, nullable=False)
    close_price: Mapped[float] = mapped_column(Float, nullable=False)
