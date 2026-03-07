from __future__ import annotations
from typing import Optional

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252
DEFAULT_RISK_FREE_RATE = 0.068  # 10Y G-sec yield default


def _daily_returns(nav_series: pd.Series) -> pd.Series:
    """Compute daily percentage returns from NAV series."""
    return nav_series.pct_change().dropna()


def compute_std_dev(nav_series: pd.Series) -> float:
    """
    Compute annualized standard deviation of daily returns.
    Returns 0.0 for zero-variance series (PPF, fixed deposits).
    """
    daily = _daily_returns(nav_series)
    if len(daily) < 2:
        return 0.0
    std = float(daily.std())
    annualized = float(std * np.sqrt(TRADING_DAYS_PER_YEAR))
    # Treat floating-point noise below 1e-10 as zero variance (e.g. PPF/FD series)
    if annualized < 1e-10:
        return 0.0
    return annualized


def compute_sharpe(nav_series: pd.Series, risk_free_rate: float = DEFAULT_RISK_FREE_RATE) -> Optional[float]:
    """
    Compute annualized Sharpe ratio.
    Returns None for zero-variance series (undefined for constant-return products).
    """
    std = compute_std_dev(nav_series)
    if std == 0.0:
        return None
    daily = _daily_returns(nav_series)
    mean_daily = float(daily.mean())
    annualized_return = mean_daily * TRADING_DAYS_PER_YEAR
    return float((annualized_return - risk_free_rate) / std)


def compute_sortino(nav_series: pd.Series, risk_free_rate: float = DEFAULT_RISK_FREE_RATE) -> Optional[float]:
    """
    Compute annualized Sortino ratio using downside deviation only.
    Returns None for zero-variance series.
    Sortino >= Sharpe when downside volatility < total volatility.
    """
    daily = _daily_returns(nav_series)
    if len(daily) < 2:
        return None
    mean_daily = float(daily.mean())
    annualized_return = mean_daily * TRADING_DAYS_PER_YEAR
    # Downside returns only (below 0)
    downside = daily[daily < 0]
    if len(downside) == 0:
        return None  # No downside — undefined
    downside_std = float(downside.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)
    if downside_std == 0.0:
        return None
    return float((annualized_return - risk_free_rate) / downside_std)


def compute_max_drawdown(nav_series: pd.Series) -> float:
    """
    Compute maximum drawdown (most negative peak-to-trough decline).
    Returns a negative float (e.g., -0.38 for a 38% drawdown).
    Returns 0.0 for flat/ascending-only series.
    """
    series = nav_series.dropna()
    if len(series) < 2:
        return 0.0
    rolling_peak = series.cummax()
    drawdown = (series - rolling_peak) / rolling_peak
    return float(drawdown.min())
