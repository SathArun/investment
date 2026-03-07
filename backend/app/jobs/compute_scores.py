"""Nightly advisor score computation job.

Iterates all tax_bracket × time_horizon combinations, builds universe vectors
from computed_metrics, and upserts advisor_scores.
"""
from __future__ import annotations
import time
from datetime import date
from typing import Optional

import structlog

from app.analytics.models import AdvisorScore, ComputedMetric
from app.analytics.score_engine import compute_advisor_score
from app.analytics.tax_engine import compute_post_tax_cagr
from app.db.base import SessionLocal

logger = structlog.get_logger()

TAX_BRACKETS = [0.0, 0.05, 0.10, 0.20, 0.30]
TIME_HORIZONS = ["short", "medium", "long"]
HOLDING_YEARS = {"short": 1, "medium": 3, "long": 5}
DEFAULT_INVESTMENT_INR = 100_000


def _get_asset_class_info(session, product_id: str, product_type: str) -> dict:
    """Return sebi_risk_level, lock_in_days, expense_ratio, asset_class_id."""
    if product_type == "mutual_fund":
        from app.market_data.models import MutualFund, AssetClass
        fund = session.get(MutualFund, product_id)
        if fund and fund.asset_class_id:
            ac = session.get(AssetClass, fund.asset_class_id)
            return {
                "sebi_risk_level": (ac.sebi_risk_level or 3) if ac else 3,
                "lock_in_days": (ac.lock_in_days if ac and ac.lock_in_days is not None else 3),
                "expense_ratio": fund.expense_ratio or (ac.expense_ratio_typical if ac else None),
                "asset_class_id": fund.asset_class_id,
            }
        return {"sebi_risk_level": 3, "lock_in_days": 3, "expense_ratio": None, "asset_class_id": product_id}
    else:
        from app.market_data.models import AssetClass
        ac = session.get(AssetClass, product_id)
        if ac:
            return {
                "sebi_risk_level": ac.sebi_risk_level or 3,
                "lock_in_days": ac.lock_in_days if ac.lock_in_days is not None else 3,
                "expense_ratio": ac.expense_ratio_typical,
                "asset_class_id": product_id,
            }
        return {"sebi_risk_level": 3, "lock_in_days": 3, "expense_ratio": None, "asset_class_id": product_id}


def _upsert_advisor_score(
    session, product_id, product_type, tax_bracket, time_horizon,
    computed_date, scores, post_tax_return_3y
):
    existing = session.get(AdvisorScore, (product_id, product_type, tax_bracket, time_horizon, computed_date))
    if existing:
        existing.score_total = scores["score_total"]
        existing.score_risk_adjusted = scores["score_risk_adjusted"]
        existing.score_tax_yield = scores["score_tax_yield"]
        existing.score_liquidity = scores["score_liquidity"]
        existing.score_expense = scores["score_expense"]
        existing.score_consistency = scores["score_consistency"]
        existing.score_goal_fit = scores["score_goal_fit"]
        existing.post_tax_return_3y = post_tax_return_3y
    else:
        session.add(AdvisorScore(
            product_id=product_id,
            product_type=product_type,
            tax_bracket=tax_bracket,
            time_horizon=time_horizon,
            computed_date=computed_date,
            score_total=scores["score_total"],
            score_risk_adjusted=scores["score_risk_adjusted"],
            score_tax_yield=scores["score_tax_yield"],
            score_liquidity=scores["score_liquidity"],
            score_expense=scores["score_expense"],
            score_consistency=scores["score_consistency"],
            score_goal_fit=scores["score_goal_fit"],
            post_tax_return_3y=post_tax_return_3y,
        ))


def compute_all_scores(session) -> dict:
    """
    Compute advisor scores for all products × all bracket+horizon combos.
    Upserts into advisor_scores. Returns summary dict.
    """
    from sqlalchemy import func
    today = date.today()

    # Fetch latest computed_metrics for each product
    latest_rows = session.query(
        ComputedMetric.product_id,
        ComputedMetric.product_type,
        func.max(ComputedMetric.computed_date).label("latest_date"),
    ).group_by(ComputedMetric.product_id, ComputedMetric.product_type).all()

    if not latest_rows:
        logger.warning("compute_scores_no_metrics_found")
        return {"total_scores": 0, "products": 0}

    all_metrics: dict[tuple, ComputedMetric] = {}
    for row in latest_rows:
        cm = session.query(ComputedMetric).filter(
            ComputedMetric.product_id == row.product_id,
            ComputedMetric.product_type == row.product_type,
            ComputedMetric.computed_date == row.latest_date,
        ).first()
        if cm:
            all_metrics[(row.product_id, row.product_type)] = cm

    total_scores = 0
    products_count = len(all_metrics)

    # Precompute asset class info for all products
    ac_infos = {
        key: _get_asset_class_info(session, key[0], key[1])
        for key in all_metrics
    }

    # Build universe vectors (bracket-independent for risk/std/expense)
    sharpe_universe = [m.sharpe_3y for m in all_metrics.values() if m.sharpe_3y is not None]
    sortino_universe = [m.sortino_3y for m in all_metrics.values() if m.sortino_3y is not None]
    std_dev_universe = [m.std_dev_3y for m in all_metrics.values() if m.std_dev_3y is not None]
    expense_universe = [
        ac_infos[key]["expense_ratio"]
        for key in all_metrics
        if ac_infos[key]["expense_ratio"] is not None
    ]

    for tax_bracket in TAX_BRACKETS:
        for time_horizon in TIME_HORIZONS:
            holding_years = HOLDING_YEARS[time_horizon]

            # Compute post-tax returns for each product (bracket+horizon specific)
            post_tax_map: dict[tuple, Optional[float]] = {}
            for key, cm in all_metrics.items():
                if cm.cagr_3y is None:
                    post_tax_map[key] = None
                    continue
                asset_class_id = ac_infos[key]["asset_class_id"]
                try:
                    result = compute_post_tax_cagr(
                        asset_class_id, cm.cagr_3y,
                        DEFAULT_INVESTMENT_INR, tax_bracket, holding_years,
                    )
                    post_tax_map[key] = result["post_tax_cagr"]
                except Exception as e:
                    logger.warning("post_tax_error", product=key[0], error=str(e))
                    post_tax_map[key] = cm.cagr_3y

            post_tax_universe = [v for v in post_tax_map.values() if v is not None]

            for key, cm in all_metrics.items():
                ac = ac_infos[key]
                scores = compute_advisor_score(
                    sharpe=cm.sharpe_3y,
                    sortino=cm.sortino_3y,
                    post_tax_return_3y=post_tax_map.get(key),
                    std_dev_3y=cm.std_dev_3y,
                    expense_ratio=ac["expense_ratio"],
                    lock_in_days=ac["lock_in_days"],
                    sebi_risk_level=ac["sebi_risk_level"],
                    time_horizon=time_horizon,
                    sharpe_universe=sharpe_universe,
                    sortino_universe=sortino_universe,
                    post_tax_universe=post_tax_universe,
                    std_dev_universe=std_dev_universe,
                    expense_universe=expense_universe,
                )
                _upsert_advisor_score(
                    session, key[0], key[1], tax_bracket, time_horizon,
                    today, scores, post_tax_map.get(key),
                )
                total_scores += 1

            session.commit()
            logger.info("compute_scores_done", tax_bracket=tax_bracket, time_horizon=time_horizon)

    logger.info("compute_scores_complete", total_scores=total_scores, products=products_count)
    return {"total_scores": total_scores, "products": products_count}


def run() -> None:
    logger.info("compute_scores_job_start")
    start = time.time()
    with SessionLocal() as session:
        result = compute_all_scores(session)
    elapsed = time.time() - start
    logger.info("compute_scores_job_done", elapsed_seconds=round(elapsed, 1), **result)


if __name__ == "__main__":
    run()
