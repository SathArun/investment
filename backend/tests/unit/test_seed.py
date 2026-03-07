"""Test reference data seeding."""
from __future__ import annotations
import pytest
from app.db.seed import seed_asset_classes, seed_tax_rules


def test_asset_classes_seeded(db_session):
    from app.market_data.models import AssetClass
    seed_asset_classes(db_session)
    total = db_session.query(AssetClass).count()
    assert total >= 15, f"Expected >= 15 asset classes in DB, got {total}"


def test_tax_rules_seeded(db_session):
    from app.analytics.models import TaxRule
    seed_tax_rules(db_session)
    total = db_session.query(TaxRule).count()
    assert total >= 8, f"Expected >= 8 tax rules in DB, got {total}"


def test_debt_mf_uses_slab_rate(db_session):
    from app.analytics.models import TaxRule
    rule = db_session.query(TaxRule).filter(
        TaxRule.asset_class_pattern == "debt_*",
        TaxRule.tax_rate_expression == "slab_rate"
    ).first()
    assert rule is not None, "Debt MF slab rate rule not found"
    assert str(rule.effective_from) >= "2023-04-01", "effective_from must be April 2023"


def test_sgb_maturity_tax_free(db_session):
    from app.analytics.models import TaxRule
    rule = db_session.query(TaxRule).filter(
        TaxRule.special_rule == "sgb_maturity_tax_free"
    ).first()
    assert rule is not None, "SGB maturity tax-free rule not found"
    assert rule.holding_period_months == 96, "SGB lock-in must be 96 months (8 years)"


def test_ppf_eee(db_session):
    from app.analytics.models import TaxRule
    rule = db_session.query(TaxRule).filter(
        TaxRule.special_rule == "ppf_eee"
    ).first()
    assert rule is not None, "PPF EEE rule not found"
    assert rule.tax_rate_expression == "0.0"


def test_fd_post_tax_at_30_bracket():
    """7% FD @ 30% bracket -> ~4.9% post-tax."""
    gross_rate = 0.07
    tax_bracket = 0.30
    post_tax = gross_rate * (1 - tax_bracket)
    assert abs(post_tax - 0.049) < 0.001, f"Expected ~4.9%, got {post_tax:.3f}"
