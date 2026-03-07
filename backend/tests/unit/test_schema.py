"""Test that all expected tables exist after migration."""
import pytest
from sqlalchemy import inspect
from app.db.base import engine

EXPECTED_TABLES = [
    "advisors", "refresh_tokens", "clients", "goals",
    "asset_classes", "mutual_funds", "nav_history", "index_history",
    "computed_metrics", "advisor_scores", "risk_profiles", "tax_rules"
]


def test_all_tables_exist():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for table in EXPECTED_TABLES:
        assert table in tables, f"Missing table: {table}"


def test_nav_history_composite_pk():
    inspector = inspect(engine)
    pk = inspector.get_pk_constraint("nav_history")
    assert set(pk["constrained_columns"]) == {"scheme_code", "nav_date"}


def test_advisor_scores_composite_pk():
    inspector = inspect(engine)
    pk = inspector.get_pk_constraint("advisor_scores")
    assert set(pk["constrained_columns"]) == {
        "product_id", "product_type", "tax_bracket", "time_horizon", "computed_date"
    }
