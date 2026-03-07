from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.analytics.risk_metrics import (
    compute_max_drawdown,
    compute_sharpe,
    compute_sortino,
    compute_std_dev,
)


# ---------------------------------------------------------------------------
# Fixture helper
# ---------------------------------------------------------------------------

def make_nav_series(
    cagr: float,
    n_days: int,
    noise_std: float = 0.0,
    start_nav: float = 100.0,
) -> pd.Series:
    daily_return = (1 + cagr) ** (1 / 252) - 1
    navs = start_nav * (1 + daily_return) ** np.arange(n_days)
    if noise_std > 0:
        np.random.seed(42)
        noise = np.random.normal(0, noise_std, n_days)
        navs = navs * (1 + noise)
    dates = pd.date_range("2019-01-01", periods=n_days, freq="B")
    return pd.Series(navs, index=dates)


def make_covid_series() -> pd.Series:
    # Pre-crash: steady growth
    pre = make_nav_series(0.12, 300)
    peak = pre.iloc[-1]
    # Crash: 38% drop
    crash_navs = np.linspace(peak, peak * 0.62, 40)
    # Recovery
    recovery = make_nav_series(0.20, 400, start_nav=peak * 0.62)
    all_navs = np.concatenate([pre.values, crash_navs, recovery.values])
    dates = pd.date_range("2019-01-01", periods=len(all_navs), freq="B")
    return pd.Series(all_navs, index=dates)


# ---------------------------------------------------------------------------
# std_dev tests
# ---------------------------------------------------------------------------

def test_std_dev_volatile_series():
    series = make_nav_series(0.12, 1260, noise_std=0.012)
    std = compute_std_dev(series)
    assert 0.1 <= std <= 0.3, f"Expected std_dev in [0.1, 0.3], got {std}"


def test_std_dev_flat_series():
    series = make_nav_series(0.07, 1260, noise_std=0.0)  # PPF-like, no noise
    std = compute_std_dev(series)
    assert std == 0.0, f"Expected 0.0 for flat series, got {std}"


# ---------------------------------------------------------------------------
# Sharpe tests
# ---------------------------------------------------------------------------

def test_sharpe_positive_for_high_return_series():
    series = make_nav_series(0.12, 1260, noise_std=0.012)
    sharpe = compute_sharpe(series)
    assert sharpe is not None
    assert sharpe > 0, f"Expected Sharpe > 0 for 12% CAGR noisy series, got {sharpe}"


def test_sharpe_none_for_flat_series():
    series = make_nav_series(0.07, 1260, noise_std=0.0)
    sharpe = compute_sharpe(series)
    assert sharpe is None, f"Expected None for flat series, got {sharpe}"


# ---------------------------------------------------------------------------
# Sortino tests
# ---------------------------------------------------------------------------

def test_sortino_gte_sharpe():
    """For a series with more positive than negative days, Sortino >= Sharpe."""
    series = make_nav_series(0.12, 1260, noise_std=0.012)
    sharpe = compute_sharpe(series)
    sortino = compute_sortino(series)
    assert sharpe is not None
    assert sortino is not None
    assert sortino >= sharpe, f"Expected Sortino ({sortino}) >= Sharpe ({sharpe})"


def test_sortino_none_for_flat_series():
    series = make_nav_series(0.07, 1260, noise_std=0.0)
    sortino = compute_sortino(series)
    assert sortino is None, f"Expected None for flat series, got {sortino}"


# ---------------------------------------------------------------------------
# Max drawdown tests
# ---------------------------------------------------------------------------

def test_max_drawdown_negative():
    series = make_nav_series(0.12, 1260, noise_std=0.012)
    mdd = compute_max_drawdown(series)
    assert mdd < 0, f"Expected max_drawdown < 0 for noisy series, got {mdd}"


def test_max_drawdown_flat():
    series = make_nav_series(0.12, 1260, noise_std=0.0)  # monotonically increasing
    mdd = compute_max_drawdown(series)
    assert mdd == 0.0, f"Expected 0.0 for flat ascending series, got {mdd}"


def test_max_drawdown_covid_simulation():
    series = make_covid_series()
    mdd = compute_max_drawdown(series)
    assert -0.42 <= mdd <= -0.34, (
        f"Expected max_drawdown in [-0.42, -0.34] for COVID simulation, got {mdd}"
    )
