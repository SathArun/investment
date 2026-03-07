from __future__ import annotations
import pytest
from app.analytics.score_engine import (
    normalize_to_percentile,
    compute_liquidity_score,
    compute_goal_fit,
    compute_advisor_score,
    WEIGHTS,
)


def test_normalize_to_percentile_known_value():
    result = normalize_to_percentile(0.8, [0, 0.2, 0.3, 0.5, 0.8, 1.1])
    assert abs(result - 83.3) <= 1.0, f"Expected ~83.3, got {result}"


def test_normalize_to_percentile_none_value():
    result = normalize_to_percentile(None, [1, 2, 3])
    assert result == 0.0


def test_liquidity_score_same_day():
    assert compute_liquidity_score(0) == 100.0


def test_liquidity_score_nps():
    assert compute_liquidity_score(-1) == 10.0


def test_liquidity_score_ppf():
    assert compute_liquidity_score(5475) == 20.0


def test_liquidity_score_equity_mf():
    assert compute_liquidity_score(3) == 75.0


def test_goal_fit_very_high_risk_long_horizon():
    assert compute_goal_fit(6, 'long') == 100.0


def test_goal_fit_low_risk_short_horizon():
    assert compute_goal_fit(1, 'short') == 100.0


def test_goal_fit_very_high_risk_short_horizon():
    assert compute_goal_fit(6, 'short') == 30.0


def test_compute_advisor_score_in_range():
    # Build a mock universe of 5 products
    sharpe_universe = [0.5, 0.8, 1.0, 1.2, 1.5]
    sortino_universe = [0.6, 0.9, 1.1, 1.3, 1.6]
    post_tax_universe = [5.0, 7.0, 9.0, 11.0, 13.0]
    std_dev_universe = [2.0, 4.0, 6.0, 8.0, 10.0]
    expense_universe = [0.5, 1.0, 1.5, 2.0, 2.5]

    result = compute_advisor_score(
        sharpe=1.0,
        sortino=1.1,
        post_tax_return_3y=9.0,
        std_dev_3y=6.0,
        expense_ratio=1.5,
        lock_in_days=3,
        sebi_risk_level=4,
        time_horizon='long',
        sharpe_universe=sharpe_universe,
        sortino_universe=sortino_universe,
        post_tax_universe=post_tax_universe,
        std_dev_universe=std_dev_universe,
        expense_universe=expense_universe,
    )

    assert 0 <= result['score_total'] <= 100, f"score_total out of range: {result['score_total']}"
    assert 'score_risk_adjusted' in result
    assert 'score_tax_yield' in result
    assert 'score_liquidity' in result
    assert 'score_expense' in result
    assert 'score_consistency' in result
    assert 'score_goal_fit' in result


def test_compute_advisor_score_weights_sum():
    total = (
        WEIGHTS['risk_adjusted'] +
        WEIGHTS['tax_yield'] +
        WEIGHTS['liquidity'] +
        WEIGHTS['expense'] +
        WEIGHTS['consistency'] +
        WEIGHTS['goal_fit']
    )
    assert abs(total - 1.0) < 1e-9, f"Weights do not sum to 1.0: {total}"


def test_ppf_gets_perfect_consistency():
    # PPF-like product with std_dev_3y=None
    result = compute_advisor_score(
        sharpe=None,
        sortino=None,
        post_tax_return_3y=7.1,
        std_dev_3y=None,
        expense_ratio=None,
        lock_in_days=5475,
        sebi_risk_level=1,
        time_horizon='long',
        sharpe_universe=[0.5, 1.0, 1.5],
        sortino_universe=[0.6, 1.1, 1.6],
        post_tax_universe=[5.0, 7.1, 9.0],
        std_dev_universe=[2.0, 5.0, 8.0],
        expense_universe=[0.5, 1.0, 1.5],
    )
    assert result['score_consistency'] == 100.0
