"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # advisors
    op.create_table(
        "advisors",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("firm_name", sa.String(), nullable=True),
        sa.Column("logo_path", sa.String(), nullable=True),
        sa.Column("primary_color", sa.String(), nullable=True),
        sa.Column("contact_phone", sa.String(), nullable=True),
        sa.Column("sebi_registration", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("advisor_id", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["advisor_id"], ["advisors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # asset_classes
    op.create_table(
        "asset_classes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("sub_category", sa.String(), nullable=True),
        sa.Column("sebi_risk_level", sa.Integer(), nullable=True),
        sa.Column("data_source", sa.String(), nullable=True),
        sa.Column("min_investment_inr", sa.Float(), nullable=True),
        sa.Column("typical_exit_load_days", sa.Integer(), nullable=True),
        sa.Column("lock_in_days", sa.Integer(), nullable=True),
        sa.Column("expense_ratio_typical", sa.Float(), nullable=True),
        sa.Column("is_crypto", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # mutual_funds
    op.create_table(
        "mutual_funds",
        sa.Column("scheme_code", sa.String(), nullable=False),
        sa.Column("scheme_name", sa.String(), nullable=False),
        sa.Column("asset_class_id", sa.String(), nullable=True),
        sa.Column("amfi_category", sa.String(), nullable=True),
        sa.Column("amc_name", sa.String(), nullable=True),
        sa.Column("direct_plan", sa.Boolean(), nullable=False),
        sa.Column("expense_ratio", sa.Float(), nullable=True),
        sa.Column("fund_manager", sa.String(), nullable=True),
        sa.Column("aum_crore", sa.Float(), nullable=True),
        sa.Column("inception_date", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["asset_class_id"], ["asset_classes.id"]),
        sa.PrimaryKeyConstraint("scheme_code"),
    )

    # nav_history (composite PK)
    op.create_table(
        "nav_history",
        sa.Column("scheme_code", sa.String(), nullable=False),
        sa.Column("nav_date", sa.Date(), nullable=False),
        sa.Column("nav", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["scheme_code"], ["mutual_funds.scheme_code"]),
        sa.PrimaryKeyConstraint("scheme_code", "nav_date"),
    )

    # index_history (composite PK)
    op.create_table(
        "index_history",
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("close_price", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("ticker", "price_date"),
    )

    # clients
    op.create_table(
        "clients",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("advisor_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("tax_bracket", sa.Float(), nullable=True),
        sa.Column("risk_category", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["advisor_id"], ["advisors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # goals
    op.create_table(
        "goals",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("advisor_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("target_amount_inr", sa.Float(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("current_corpus_inr", sa.Float(), nullable=True),
        sa.Column("monthly_sip_inr", sa.Float(), nullable=True),
        sa.Column("annual_stepup_pct", sa.Float(), nullable=True),
        sa.Column("inflation_rate", sa.Float(), nullable=True),
        sa.Column("expected_return_rate", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["advisor_id"], ["advisors.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # risk_profiles
    op.create_table(
        "risk_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("advisor_id", sa.String(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("risk_category", sa.String(), nullable=False),
        sa.Column("question_responses", sa.Text(), nullable=True),
        sa.Column("advisor_rationale", sa.Text(), nullable=False),
        sa.Column("compliance_pdf_path", sa.String(), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("retention_until", sa.Date(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["advisor_id"], ["advisors.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # computed_metrics (composite PK)
    op.create_table(
        "computed_metrics",
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("product_type", sa.String(), nullable=False),
        sa.Column("computed_date", sa.Date(), nullable=False),
        sa.Column("cagr_1y", sa.Float(), nullable=True),
        sa.Column("cagr_3y", sa.Float(), nullable=True),
        sa.Column("cagr_5y", sa.Float(), nullable=True),
        sa.Column("cagr_10y", sa.Float(), nullable=True),
        sa.Column("std_dev_3y", sa.Float(), nullable=True),
        sa.Column("sharpe_3y", sa.Float(), nullable=True),
        sa.Column("sortino_3y", sa.Float(), nullable=True),
        sa.Column("max_drawdown_5y", sa.Float(), nullable=True),
        sa.Column("expense_ratio", sa.Float(), nullable=True),
        sa.Column("sharpe_ratio", sa.Float(), nullable=True),
        sa.Column("sortino_ratio", sa.Float(), nullable=True),
        sa.Column("max_drawdown", sa.Float(), nullable=True),
        sa.Column("std_dev_annual", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("product_id", "product_type", "computed_date"),
    )

    # advisor_scores (composite PK)
    op.create_table(
        "advisor_scores",
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("product_type", sa.String(), nullable=False),
        sa.Column("tax_bracket", sa.Float(), nullable=False),
        sa.Column("time_horizon", sa.String(), nullable=False),
        sa.Column("computed_date", sa.Date(), nullable=False),
        sa.Column("score_total", sa.Float(), nullable=True),
        sa.Column("score_risk_adjusted", sa.Float(), nullable=True),
        sa.Column("score_tax_yield", sa.Float(), nullable=True),
        sa.Column("score_liquidity", sa.Float(), nullable=True),
        sa.Column("score_expense", sa.Float(), nullable=True),
        sa.Column("score_consistency", sa.Float(), nullable=True),
        sa.Column("score_goal_fit", sa.Float(), nullable=True),
        sa.Column("post_tax_return_3y", sa.Float(), nullable=True),
        sa.Column("risk_adjusted_score", sa.Float(), nullable=True),
        sa.Column("tax_adjusted_score", sa.Float(), nullable=True),
        sa.Column("liquidity_score", sa.Float(), nullable=True),
        sa.Column("cost_score", sa.Float(), nullable=True),
        sa.Column("consistency_score", sa.Float(), nullable=True),
        sa.Column("goal_fit_score", sa.Float(), nullable=True),
        sa.Column("total_score", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint(
            "product_id", "product_type", "tax_bracket", "time_horizon", "computed_date"
        ),
    )

    # tax_rules
    op.create_table(
        "tax_rules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("asset_class_pattern", sa.String(), nullable=False),
        sa.Column("holding_period_type", sa.String(), nullable=True),
        sa.Column("holding_period_months", sa.Integer(), nullable=True),
        sa.Column("tax_rate_expression", sa.String(), nullable=False),
        sa.Column("annual_exemption_inr", sa.Float(), nullable=True),
        sa.Column("special_rule", sa.String(), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tax_rules")
    op.drop_table("advisor_scores")
    op.drop_table("computed_metrics")
    op.drop_table("risk_profiles")
    op.drop_table("goals")
    op.drop_table("clients")
    op.drop_table("index_history")
    op.drop_table("nav_history")
    op.drop_table("mutual_funds")
    op.drop_table("asset_classes")
    op.drop_table("refresh_tokens")
    op.drop_table("advisors")
