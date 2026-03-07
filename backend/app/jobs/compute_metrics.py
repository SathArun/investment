from __future__ import annotations
import time
from datetime import date
from typing import Optional

import pandas as pd
import structlog

from app.analytics.returns import compute_cagr, compute_rolling_returns, get_nav_series
from app.analytics.risk_metrics import compute_std_dev, compute_sharpe, compute_sortino, compute_max_drawdown
from app.analytics.models import ComputedMetric
from app.db.base import SessionLocal

logger = structlog.get_logger()

RISK_FREE_RATE = 0.068  # 10Y G-sec yield; update when RBI changes rates


def _compute_metrics_for_series(nav_series: pd.Series) -> dict:
    """Compute all metrics for a given NAV/price series."""
    return {
        "cagr_1y": compute_cagr(nav_series, 1),
        "cagr_3y": compute_cagr(nav_series, 3),
        "cagr_5y": compute_cagr(nav_series, 5),
        "cagr_10y": compute_cagr(nav_series, 10),
        "std_dev_3y": _compute_with_window(nav_series, compute_std_dev, 3),
        "sharpe_3y": _compute_with_window(nav_series, lambda s: compute_sharpe(s, RISK_FREE_RATE), 3),
        "sortino_3y": _compute_with_window(nav_series, lambda s: compute_sortino(s, RISK_FREE_RATE), 3),
        "max_drawdown_5y": _compute_with_window(nav_series, compute_max_drawdown, 5),
    }


def _compute_with_window(nav_series: pd.Series, fn, years: int) -> Optional[float]:
    """Apply fn to last N years of data. Returns None if insufficient data."""
    required = years * 252
    series = nav_series.dropna().sort_index()
    if len(series) < required:
        return None
    windowed = series.iloc[-required:]
    try:
        return fn(windowed)
    except Exception as e:
        logger.warning("metric_compute_error", error=str(e))
        return None


def compute_all_product_metrics(session) -> dict:
    """
    Compute metrics for all active mutual funds and index products.
    Upserts into computed_metrics table.
    Returns summary dict.
    """
    from app.market_data.models import MutualFund, AssetClass, IndexHistory

    today = date.today()
    processed = 0
    skipped = 0
    errors = 0

    # 1. Process mutual funds
    funds = session.query(MutualFund).filter(MutualFund.is_active == True).all()
    logger.info("compute_metrics_start", mutual_funds=len(funds))

    for i, fund in enumerate(funds):
        try:
            nav_series = get_nav_series(fund.scheme_code, "mutual_fund", session)
            if nav_series is None or len(nav_series) < 252:
                skipped += 1
                continue

            metrics = _compute_metrics_for_series(nav_series)
            _upsert_computed_metric(session, fund.scheme_code, "mutual_fund", today, metrics, fund.expense_ratio)
            processed += 1

            if (i + 1) % 100 == 0:
                logger.info("compute_metrics_progress", processed=processed, total=len(funds))
                session.commit()
        except Exception as e:
            logger.error("compute_metrics_fund_error", scheme_code=fund.scheme_code, error=str(e))
            errors += 1

    session.commit()

    # 2. Process index tickers (from index_history)
    tickers = session.query(IndexHistory.ticker).distinct().all()
    tickers = [t[0] for t in tickers if not t[0].startswith("NPS_")]  # Skip NPS synthetic tickers
    logger.info("compute_metrics_index_start", tickers=len(tickers))

    for ticker in tickers:
        try:
            nav_series = get_nav_series(ticker, "index", session)
            if nav_series is None or len(nav_series) < 252:
                skipped += 1
                continue

            metrics = _compute_metrics_for_series(nav_series)
            _upsert_computed_metric(session, ticker, "index", today, metrics, None)
            processed += 1
        except Exception as e:
            logger.error("compute_metrics_index_error", ticker=ticker, error=str(e))
            errors += 1

    session.commit()
    result = {"processed": processed, "skipped": skipped, "errors": errors}
    logger.info("compute_metrics_complete", **result)
    return result


def _upsert_computed_metric(session, product_id: str, product_type: str, computed_date: date, metrics: dict, expense_ratio):
    """INSERT OR REPLACE into computed_metrics."""
    existing = session.get(ComputedMetric, (product_id, product_type, computed_date))
    if existing:
        for k, v in metrics.items():
            setattr(existing, k, v)
        existing.expense_ratio = expense_ratio
    else:
        row = ComputedMetric(
            product_id=product_id,
            product_type=product_type,
            computed_date=computed_date,
            expense_ratio=expense_ratio,
            **metrics,
        )
        session.add(row)


def run() -> None:
    """Main entry point for nightly metrics job."""
    logger.info("compute_metrics_job_start")
    start = time.time()
    with SessionLocal() as session:
        result = compute_all_product_metrics(session)
    elapsed = time.time() - start
    logger.info("compute_metrics_job_done", elapsed_seconds=round(elapsed, 1), **result)


if __name__ == "__main__":
    run()
