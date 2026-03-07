from __future__ import annotations

from datetime import date

import pytest

from app.analytics.tax_engine import compute_post_tax_cagr, load_tax_rules


# ---------------------------------------------------------------------------
# Scenario 1: FD at 30% bracket, 3Y hold, 7% pre-tax
# post-tax ≈ 7% × 0.70 = 4.9%
# (exact: gain taxed at 30% each year via corpus approach)
# ---------------------------------------------------------------------------
def test_fd_slab_rate_30pct():
    """FD: 7% pre-tax, 30% bracket, 3Y → post-tax close to 4.9%."""
    result = compute_post_tax_cagr("fd", 0.07, 100_000, 0.30, 3)
    assert result["post_tax_cagr"] is not None
    # Effective tax rate should be ~30% (slab rate applied to entire gain)
    assert abs(result["effective_tax_rate"] - 0.30) < 0.02
    # Post-tax CAGR between 0.044 and 0.054
    assert 0.044 <= result["post_tax_cagr"] <= 0.054


# ---------------------------------------------------------------------------
# Scenario 2: PPF → completely tax-free (EEE)
# ---------------------------------------------------------------------------
def test_ppf_eee_tax_free():
    """PPF: EEE — post-tax CAGR equals pre-tax CAGR, no tax."""
    result = compute_post_tax_cagr("ppf", 0.071, 100_000, 0.30, 15)
    assert abs(result["post_tax_cagr"] - 0.071) < 0.001
    assert result["effective_tax_rate"] == 0.0
    desc = result.get("tax_description", "")
    assert "EEE" in desc or "Tax Free" in desc or "tax_free" in desc.lower() or "free" in desc.lower()


# ---------------------------------------------------------------------------
# Scenario 3: Equity MF LTCG, 2Y, 12% pre-tax, Rs 1L investment
# gain = 100000*(1.12^2 - 1) ≈ 25,440 < exemption 1,25,000 → tax = 0
# ---------------------------------------------------------------------------
def test_equity_mf_ltcg_under_exemption():
    """Equity LTCG: gain < Rs 1.25L exemption → zero tax, post-tax ≈ pre-tax."""
    result = compute_post_tax_cagr("eq_largecap", 0.12, 100_000, 0.30, 2)
    # No tax owed since gain is below the annual exemption
    assert result["effective_tax_rate"] == 0.0 or result["effective_tax_rate"] < 0.01
    assert 0.115 <= result["post_tax_cagr"] <= 0.125


# ---------------------------------------------------------------------------
# Scenario 4: Equity MF STCG, 6-month hold, 20% pre-tax return
# STCG at 20% flat on entire gain
# ---------------------------------------------------------------------------
def test_equity_mf_stcg_20pct():
    """Equity STCG: 20% flat tax on short-term gain (< 12 months)."""
    result = compute_post_tax_cagr("eq_largecap", 0.20, 100_000, 0.30, 0.5)
    assert abs(result["effective_tax_rate"] - 0.20) < 0.01


# ---------------------------------------------------------------------------
# Scenario 5: Debt MF, 3Y hold, 30% bracket, 7% return (post-April 2023)
# Slab rate on ALL gains (no LTCG benefit)
# ---------------------------------------------------------------------------
def test_debt_mf_slab_rate():
    """Debt MF post-2023: slab rate (30%) on all gains regardless of holding."""
    result = compute_post_tax_cagr("debt_shortterm", 0.07, 100_000, 0.30, 3)
    assert abs(result["effective_tax_rate"] - 0.30) < 0.02
    # Rule ID or description should indicate slab treatment
    rule_id = result.get("rule_id", "")
    description = result.get("tax_description", "")
    assert "slab" in rule_id.lower() or "slab" in description.lower() or "Debt" in description


# ---------------------------------------------------------------------------
# Scenario 6: Gold ETF, 2Y hold, 12% CAGR → 12.5% LTCG, no exemption
# ---------------------------------------------------------------------------
def test_gold_etf_ltcg_125pct():
    """Gold ETF LTCG (>12M): 12.5% tax on full gain, no exemption."""
    result = compute_post_tax_cagr("gold_etf", 0.12, 100_000, 0.30, 2)
    assert abs(result["effective_tax_rate"] - 0.125) < 0.01


# ---------------------------------------------------------------------------
# Scenario 7: SGB, 8Y hold at maturity → completely tax-free
# ---------------------------------------------------------------------------
def test_sgb_maturity_tax_free():
    """SGB at 8-year maturity: capital gains fully tax-free."""
    result = compute_post_tax_cagr("gold_sgb", 0.12, 100_000, 0.30, 8)
    assert abs(result["post_tax_cagr"] - 0.12) < 0.001
    assert result["effective_tax_rate"] == 0.0


# ---------------------------------------------------------------------------
# Scenario 8: SGB early exit, 5Y hold → 12.5% LTCG
# ---------------------------------------------------------------------------
def test_sgb_premature_exit_ltcg():
    """SGB premature exit (5Y < 8Y): 12.5% LTCG applies."""
    result = compute_post_tax_cagr("gold_sgb", 0.12, 100_000, 0.30, 5)
    assert abs(result["effective_tax_rate"] - 0.125) < 0.01


# ---------------------------------------------------------------------------
# Scenario 9: Tax rules loaded from JSON — basic sanity checks
# ---------------------------------------------------------------------------
def test_load_tax_rules_returns_valid_rules():
    """load_tax_rules() returns >= 8 rules, each with asset_class_pattern."""
    rules = load_tax_rules()
    assert len(rules) >= 8
    for rule in rules:
        assert "asset_class_pattern" in rule, f"Rule missing asset_class_pattern: {rule}"
        assert rule["asset_class_pattern"], f"Rule has empty asset_class_pattern: {rule}"


# ---------------------------------------------------------------------------
# Scenario 10: effective_from filtering
# Debt MF slab rule effective 2023-04-01 must NOT appear for date 2022-01-01
# ---------------------------------------------------------------------------
def test_effective_from_filtering_excludes_future_rule():
    """Rules with effective_from after as_of_date must be excluded."""
    old_date = date(2022, 1, 1)
    rules = load_tax_rules(as_of_date=old_date)
    rule_ids = [r["id"] for r in rules]
    assert "debt_mf_slab_2023" not in rule_ids, (
        "debt_mf_slab_2023 (effective 2023-04-01) should not appear for 2022-01-01"
    )
