"""ORM models for computed metrics, advisor scores, and tax rules."""
from __future__ import annotations
from datetime import date

from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ComputedMetric(Base):
    __tablename__ = "computed_metrics"

    product_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    product_type: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    computed_date: Mapped[date] = mapped_column(Date, primary_key=True, nullable=False)
    cagr_1y: Mapped[float | None] = mapped_column(Float, nullable=True)
    cagr_3y: Mapped[float | None] = mapped_column(Float, nullable=True)
    cagr_5y: Mapped[float | None] = mapped_column(Float, nullable=True)
    cagr_10y: Mapped[float | None] = mapped_column(Float, nullable=True)
    std_dev_3y: Mapped[float | None] = mapped_column(Float, nullable=True)
    sharpe_3y: Mapped[float | None] = mapped_column(Float, nullable=True)
    sortino_3y: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_drawdown_5y: Mapped[float | None] = mapped_column(Float, nullable=True)
    expense_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Aliases used in task spec mapping
    sharpe_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    sortino_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Float, nullable=True)
    std_dev_annual: Mapped[float | None] = mapped_column(Float, nullable=True)


class AdvisorScore(Base):
    __tablename__ = "advisor_scores"

    product_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    product_type: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    tax_bracket: Mapped[float] = mapped_column(Float, primary_key=True, nullable=False)
    time_horizon: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    computed_date: Mapped[date] = mapped_column(Date, primary_key=True, nullable=False)
    score_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_risk_adjusted: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_tax_yield: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_liquidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_expense: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_consistency: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_goal_fit: Mapped[float | None] = mapped_column(Float, nullable=True)
    post_tax_return_3y: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Aliases used in task spec
    risk_adjusted_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    tax_adjusted_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    liquidity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    consistency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    goal_fit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class TaxRule(Base):
    __tablename__ = "tax_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    asset_class_pattern: Mapped[str] = mapped_column(String, nullable=False)
    holding_period_type: Mapped[str | None] = mapped_column(String, nullable=True)
    holding_period_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tax_rate_expression: Mapped[str] = mapped_column(String, nullable=False)
    annual_exemption_inr: Mapped[float | None] = mapped_column(Float, nullable=True)
    special_rule: Mapped[str | None] = mapped_column(String, nullable=True)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
