from __future__ import annotations
import math
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd
import structlog

logger = structlog.get_logger()

TRADING_DAYS_PER_YEAR = 252


def compute_cagr(nav_series: pd.Series, years: int) -> Optional[float]:
    """
    Compute CAGR over the last `years` years of NAV data.
    Returns None if fewer than years*252 data points are available.
    nav_series: pandas Series with datetime index, values are NAV prices.
    """
    required_points = years * TRADING_DAYS_PER_YEAR
    if len(nav_series) < required_points:
        return None
    series = nav_series.dropna().sort_index()
    if len(series) < required_points:
        return None
    end_val = series.iloc[-1]
    start_val = series.iloc[-required_points]
    if start_val <= 0:
        return None
    # Use integer years: for trading-day series (252/year), this is accurate.
    # actual calendar elapsed ≈ years * 365 days, so 1/years is correct.
    return float((end_val / start_val) ** (1.0 / years) - 1)


def annualize_return(period_return: float, years: float) -> float:
    """Convert a total return over `years` to an annualized rate."""
    if years <= 0:
        raise ValueError("years must be positive")
    return float((1 + period_return) ** (1.0 / years) - 1)


def compute_rolling_returns(nav_series: pd.Series, window_years: int = 1) -> pd.Series:
    """
    Compute rolling CAGR over a window of window_years.
    Returns a Series of annualized returns.
    Length ≈ len(nav_series) - window_years * TRADING_DAYS_PER_YEAR
    """
    window = window_years * TRADING_DAYS_PER_YEAR
    series = nav_series.dropna().sort_index()
    if len(series) <= window:
        return pd.Series(dtype=float)
    rolling_return = (series / series.shift(window)) ** (1.0 / window_years) - 1
    return rolling_return.dropna()


def get_nav_series(product_id: str, product_type: str, session) -> Optional[pd.Series]:
    """
    Fetch NAV/price history from DB for the given product.
    product_type: 'mutual_fund' | 'index' | 'ppf' | 'fd'
    Returns a pandas Series with date index and close_price/nav values, or None.
    """
    if product_type == "mutual_fund":
        from app.market_data.models import NavHistory
        rows = session.query(NavHistory).filter(
            NavHistory.scheme_code == product_id
        ).order_by(NavHistory.nav_date).all()
        if not rows:
            return None
        dates = [r.nav_date for r in rows]
        values = [r.nav for r in rows]
        return pd.Series(values, index=pd.DatetimeIndex(dates))
    elif product_type == "index":
        from app.market_data.models import IndexHistory
        rows = session.query(IndexHistory).filter(
            IndexHistory.ticker == product_id
        ).order_by(IndexHistory.price_date).all()
        if not rows:
            return None
        dates = [r.price_date for r in rows]
        values = [r.close_price for r in rows]
        return pd.Series(values, index=pd.DatetimeIndex(dates))
    else:
        logger.warning("get_nav_series_unknown_type", product_type=product_type)
        return None
