"""Unit tests for goal planner computation — no DB required."""
from __future__ import annotations
import types
from datetime import date, timedelta

import pytest

from app.goals.service import (
    ALLOCATION_RULES,
    RETURN_SCENARIOS,
    _fv_lumpsum,
    _fv_sip_with_stepup,
    _required_sip,
    compute_goal_plan,
)


# ---------------------------------------------------------------------------
# Helpers to build mock Goal / Client without SQLAlchemy
# ---------------------------------------------------------------------------

def _make_goal(
    *,
    target_amount_inr: float = 2_500_000,
    target_date: date | None = None,
    current_corpus_inr: float = 0.0,
    monthly_sip_inr: float = 0.0,
    annual_stepup_pct: float = 0.0,
    inflation_rate: float = 0.06,
    years_from_now: int | None = None,
) -> types.SimpleNamespace:
    if target_date is None and years_from_now is not None:
        target_date = date.today() + timedelta(days=years_from_now * 365)
    return types.SimpleNamespace(
        target_amount_inr=target_amount_inr,
        target_date=target_date,
        current_corpus_inr=current_corpus_inr,
        monthly_sip_inr=monthly_sip_inr,
        annual_stepup_pct=annual_stepup_pct,
        inflation_rate=inflation_rate,
    )


def _make_client(*, tax_bracket: float = 0.0) -> types.SimpleNamespace:
    return types.SimpleNamespace(tax_bracket=tax_bracket)


# ---------------------------------------------------------------------------
# Test 1: inflation-adjusted target exceeds nominal target
# ---------------------------------------------------------------------------

def test_inflation_adjusted_target():
    goal = _make_goal(target_amount_inr=2_500_000, inflation_rate=0.06, years_from_now=15)
    client = _make_client()
    result = compute_goal_plan(goal, client)
    assert result["inflation_adjusted_target"] > 2_500_000


# ---------------------------------------------------------------------------
# Test 2: SIP with 10% step-up produces higher FV than 0% step-up
# ---------------------------------------------------------------------------

def test_stepup_sip_higher_than_no_stepup():
    fv_stepup = _fv_sip_with_stepup(10_000, 0.12, 15, 0.10)
    fv_no_stepup = _fv_sip_with_stepup(10_000, 0.12, 15, 0.0)
    assert fv_stepup > fv_no_stepup


# ---------------------------------------------------------------------------
# Test 3: NPS highlight is True for long horizon + high tax bracket
# ---------------------------------------------------------------------------

def test_nps_highlight_long_high_bracket():
    goal = _make_goal(years_from_now=15)
    client = _make_client(tax_bracket=0.30)
    result = compute_goal_plan(goal, client)
    assert result["nps_highlight"] is True


# ---------------------------------------------------------------------------
# Test 4: NPS highlight is False for short horizon even with high tax bracket
# ---------------------------------------------------------------------------

def test_nps_highlight_false_short():
    goal = _make_goal(years_from_now=5)
    client = _make_client(tax_bracket=0.30)
    result = compute_goal_plan(goal, client)
    assert result["nps_highlight"] is False


# ---------------------------------------------------------------------------
# Test 5: Allocation percentages sum to 100 for every horizon bucket
# ---------------------------------------------------------------------------

def test_recommended_allocation_sums_to_100():
    for horizon, buckets in ALLOCATION_RULES.items():
        total = sum(b["pct"] for b in buckets)
        assert total == 100, f"Horizon '{horizon}' pct sum is {total}, expected 100"


# ---------------------------------------------------------------------------
# Test 6: gap_amount == 0 and required_sip == 0 when corpus is on track
# ---------------------------------------------------------------------------

def test_gap_zero_when_on_track():
    # Large corpus + large SIP should exceed the target
    goal = _make_goal(
        target_amount_inr=1_000_000,
        inflation_rate=0.06,
        years_from_now=10,
        current_corpus_inr=5_000_000,  # already way above target
        monthly_sip_inr=50_000,
    )
    client = _make_client()
    result = compute_goal_plan(goal, client)
    assert result["gap_amount"] == 0
    assert result["required_sip"] == 0


# ---------------------------------------------------------------------------
# Test 7: corpus_projection length equals the number of years to target
# ---------------------------------------------------------------------------

def test_corpus_projection_length():
    years = 12
    goal = _make_goal(years_from_now=years, monthly_sip_inr=5_000)
    client = _make_client()
    result = compute_goal_plan(goal, client)
    assert len(result["corpus_projection"]) == years


# ---------------------------------------------------------------------------
# Test 8: required_sip is positive when there is a gap
# ---------------------------------------------------------------------------

def test_required_sip_positive_when_gap():
    # Tiny corpus, high target, short horizon — guaranteed gap
    goal = _make_goal(
        target_amount_inr=10_000_000,
        inflation_rate=0.06,
        years_from_now=5,
        current_corpus_inr=0,
        monthly_sip_inr=0,
    )
    client = _make_client()
    result = compute_goal_plan(goal, client)
    assert result["gap_amount"] > 0
    assert result["required_sip"] > 0
