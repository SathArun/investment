from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.analytics.returns import (
    annualize_return,
    compute_cagr,
    compute_rolling_returns,
    TRADING_DAYS_PER_YEAR,
)


def make_nav_series(cagr: float, n_days: int, start_nav: float = 100.0) -> pd.Series:
    daily_return = (1 + cagr) ** (1 / 252) - 1
    navs = start_nav * (1 + daily_return) ** np.arange(n_days)
    dates = pd.date_range("2019-01-01", periods=n_days, freq="B")
    return pd.Series(navs, index=dates)


def test_compute_cagr_5y_synthetic():
    """5-year synthetic series at 12% CAGR — result should be between 0.11 and 0.13."""
    series = make_nav_series(cagr=0.12, n_days=1260)
    result = compute_cagr(series, years=5)
    assert result is not None
    assert 0.11 < result < 0.13


def test_compute_cagr_returns_none_if_insufficient_history():
    """500-point series requesting 3Y CAGR (756 points needed) → None."""
    series = make_nav_series(cagr=0.10, n_days=500)
    result = compute_cagr(series, years=3)
    assert result is None


def test_compute_cagr_1y():
    """252-point series at 15% CAGR — assert within 1% tolerance."""
    series = make_nav_series(cagr=0.15, n_days=252)
    result = compute_cagr(series, years=1)
    assert result is not None
    assert abs(result - 0.15) < 0.01


def test_compute_cagr_3y():
    """756-point series at 10% CAGR — assert within 1% tolerance."""
    series = make_nav_series(cagr=0.10, n_days=756)
    result = compute_cagr(series, years=3)
    assert result is not None
    assert abs(result - 0.10) < 0.01


def test_compute_cagr_flat_rate():
    """Simulate PPF constant growth at 7.1% — CAGR should be approx 0.071 ±0.002."""
    series = make_nav_series(cagr=0.071, n_days=1260)
    result = compute_cagr(series, years=5)
    assert result is not None
    assert abs(result - 0.071) < 0.002


def test_rolling_returns_length():
    """1260-point series, window=1y → result length approx 1260-252 (within ±5)."""
    series = make_nav_series(cagr=0.12, n_days=1260)
    result = compute_rolling_returns(series, window_years=1)
    expected_len = 1260 - TRADING_DAYS_PER_YEAR
    assert abs(len(result) - expected_len) <= 5


def test_rolling_returns_empty_if_too_short():
    """100-point series with window=1y (252 points needed) → empty Series."""
    series = make_nav_series(cagr=0.10, n_days=100)
    result = compute_rolling_returns(series, window_years=1)
    assert isinstance(result, pd.Series)
    assert len(result) == 0


def test_annualize_return():
    """total_return=0.2629 over 2 years → approx 0.12 CAGR."""
    result = annualize_return(period_return=0.2629, years=2)
    assert abs(result - 0.12) < 0.005
