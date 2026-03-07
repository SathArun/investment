from __future__ import annotations
from datetime import date, timedelta
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func

from app.analytics.models import AdvisorScore, ComputedMetric
from app.market_data.models import AssetClass, MutualFund, NavHistory, IndexHistory


SEBI_RISK_LABELS = {
    1: "Low", 2: "Low to Moderate", 3: "Moderate",
    4: "Moderately High", 5: "High", 6: "Very High",
}

LIQUIDITY_LABELS = {
    (0, 0): "Same Day",
    (1, 1): "T+1",
    (2, 3): "T+2-3",
    (4, 365): "7-15 Days",
}


def _get_liquidity_label(lock_in_days: int) -> str:
    if lock_in_days == 0:
        return "Same Day"
    if lock_in_days <= 1:
        return "T+1"
    if lock_in_days <= 3:
        return "T+2-3"
    if lock_in_days == -1 or lock_in_days >= 5475:
        return "Lock-in"
    return "7-15 Days"


def get_latest_job_timestamps(session: Session) -> dict:
    """Get latest data freshness timestamps from index_history and nav_history."""
    from sqlalchemy import func
    amfi_latest = session.query(func.max(NavHistory.nav_date)).scalar()
    equity_latest = session.query(func.max(IndexHistory.price_date)).filter(
        ~IndexHistory.ticker.startswith("NPS_")
    ).scalar()
    nps_latest = session.query(func.max(IndexHistory.price_date)).filter(
        IndexHistory.ticker.startswith("NPS_")
    ).scalar()

    def _fmt(d) -> Optional[str]:
        return d.isoformat() if d else None

    today = date.today()
    stale_threshold = timedelta(hours=48)

    def _is_stale(d) -> bool:
        if d is None:
            return True
        return (today - d).total_seconds() > stale_threshold.total_seconds()

    return {
        "amfi": _fmt(amfi_latest),
        "equity": _fmt(equity_latest),
        "nps": _fmt(nps_latest),
        "amfi_stale": _is_stale(amfi_latest),
        "equity_stale": _is_stale(equity_latest),
        "nps_stale": _is_stale(nps_latest),
    }


def get_products(
    session: Session,
    tax_bracket: float = 0.30,
    time_horizon: str = "long",
    risk_filter: Optional[str] = None,
    sort_by: str = "score_total",
    sort_dir: str = "desc",
) -> dict:
    """
    Query advisor_scores + computed_metrics + asset_classes.
    Returns {products: [...], data_freshness: {...}}
    Falls back to yesterday's scores if today's not found.
    """
    today = date.today()

    latest_date = session.query(func.max(AdvisorScore.computed_date)).filter(
        AdvisorScore.tax_bracket == tax_bracket,
        AdvisorScore.time_horizon == time_horizon,
        AdvisorScore.computed_date >= today - timedelta(days=7),
    ).scalar()

    scores = []
    if latest_date:
        scores = session.query(AdvisorScore).filter(
            AdvisorScore.tax_bracket == tax_bracket,
            AdvisorScore.time_horizon == time_horizon,
            AdvisorScore.computed_date == latest_date,
        ).all()

    if not scores:
        return {"products": [], "data_freshness": get_latest_job_timestamps(session)}

    # Bulk-fetch all related data to avoid N+1 queries
    all_product_ids = [s.product_id for s in scores]
    fund_ids = [s.product_id for s in scores if s.product_type == "mutual_fund"]

    funds_by_id: dict = {}
    if fund_ids:
        funds_by_id = {f.scheme_code: f for f in session.query(MutualFund).filter(MutualFund.scheme_code.in_(fund_ids)).all()}

    ac_ids = list({f.asset_class_id for f in funds_by_id.values() if f.asset_class_id}
                  | {s.product_id for s in scores if s.product_type != "mutual_fund"})
    acs_by_id: dict = {}
    if ac_ids:
        acs_by_id = {a.id: a for a in session.query(AssetClass).filter(AssetClass.id.in_(ac_ids)).all()}

    cms_by_id: dict = {}
    if all_product_ids:
        all_cms = (session.query(ComputedMetric)
                   .filter(ComputedMetric.product_id.in_(all_product_ids))
                   .order_by(desc(ComputedMetric.computed_date))
                   .all())
        for cm in all_cms:
            if cm.product_id not in cms_by_id:
                cms_by_id[cm.product_id] = cm

    products = []
    for score in scores:
        cm = cms_by_id.get(score.product_id)

        # Get asset class info
        if score.product_type == "mutual_fund":
            fund = funds_by_id.get(score.product_id)
            asset_class = acs_by_id.get(fund.asset_class_id) if (fund and fund.asset_class_id) else None
            name = fund.scheme_name if fund else score.product_id
            expense_ratio = fund.expense_ratio if fund else None
        else:
            asset_class = acs_by_id.get(score.product_id)
            name = asset_class.name if asset_class else score.product_id
            expense_ratio = asset_class.expense_ratio_typical if asset_class else None

        sebi_risk_level = asset_class.sebi_risk_level if asset_class else None
        lock_in_days = asset_class.lock_in_days if asset_class else 0
        category = asset_class.category if asset_class else "Unknown"

        # Apply risk filter
        if risk_filter and risk_filter != "all":
            # Conservative: up to Low-to-Moderate (level 2)
            # Moderate: up to Moderately High (level 4, per SEBI category definitions)
            # Aggressive: all levels
            risk_map = {"Conservative": 2, "Moderate": 4, "Aggressive": 6}
            max_risk = risk_map.get(risk_filter, 6)
            if sebi_risk_level and sebi_risk_level > max_risk:
                continue

        row = {
            "id": score.product_id,
            "name": name,
            "asset_class": score.product_id if score.product_type == "index" else (asset_class.id if asset_class else None),
            "category": category,
            "sebi_risk_level": sebi_risk_level,
            "sebi_risk_label": SEBI_RISK_LABELS.get(sebi_risk_level, "Unknown") if sebi_risk_level else None,
            "cagr_1y": cm.cagr_1y if cm else None,
            "cagr_3y": cm.cagr_3y if cm else None,
            "cagr_5y": cm.cagr_5y if cm else None,
            "cagr_10y": cm.cagr_10y if cm else None,
            "std_dev_3y": cm.std_dev_3y if cm else None,
            "sharpe_3y": cm.sharpe_3y if cm else None,
            "max_drawdown_5y": cm.max_drawdown_5y if cm else None,
            "post_tax_return_3y": score.post_tax_return_3y,
            "expense_ratio": expense_ratio,
            "min_investment_inr": asset_class.min_investment_inr if asset_class else None,
            "liquidity_label": _get_liquidity_label(lock_in_days if lock_in_days is not None else 0),
            "advisor_score": score.score_total,
            "score_breakdown": {
                "risk_adjusted": score.score_risk_adjusted,
                "tax_yield": score.score_tax_yield,
                "liquidity": score.score_liquidity,
                "expense": score.score_expense,
                "consistency": score.score_consistency,
                "goal_fit": score.score_goal_fit,
            },
            "is_crypto": asset_class.is_crypto if asset_class else False,
            "data_available_since": None,
        }
        products.append(row)

    # Sort
    valid_sort_fields = {"score_total", "cagr_1y", "cagr_3y", "cagr_5y", "cagr_10y", "std_dev_3y", "advisor_score"}
    if sort_by not in valid_sort_fields:
        sort_by = "score_total"

    reverse = sort_dir != "asc"
    products.sort(
        key=lambda p: (p.get(sort_by) is None, p.get(sort_by) or 0),
        reverse=reverse,
    )

    return {
        "products": products,
        "data_freshness": get_latest_job_timestamps(session),
    }


def get_product_history(session: Session, product_id: str, period: str = "5y") -> Optional[dict]:
    """
    Get NAV/price history and rolling 1Y returns for a product.
    Tries nav_history first, then index_history.
    Returns None if product not found.
    """
    from app.analytics.returns import compute_rolling_returns

    period_years = {"1y": 1, "3y": 3, "5y": 5, "10y": 10}.get(period, 5)
    cutoff = date.today() - timedelta(days=period_years * 365)

    # Try mutual fund NAV
    rows = session.query(NavHistory.nav_date, NavHistory.nav).filter(
        NavHistory.scheme_code == product_id,
        NavHistory.nav_date >= cutoff,
    ).order_by(NavHistory.nav_date).all()

    if not rows:
        # Try index history
        rows = session.query(IndexHistory.price_date, IndexHistory.close_price).filter(
            IndexHistory.ticker == product_id,
            IndexHistory.price_date >= cutoff,
        ).order_by(IndexHistory.price_date).all()
        if not rows:
            return None
        dates = [r[0] for r in rows]
        values = [r[1] for r in rows]
    else:
        dates = [r[0] for r in rows]
        values = [r[1] for r in rows]

    returns_series = [{"date": d.isoformat(), "value": v} for d, v in zip(dates, values)]

    # Compute rolling 1Y returns
    nav_series = pd.Series(values, index=pd.DatetimeIndex(dates))
    rolling = compute_rolling_returns(nav_series, window_years=1)
    rolling_1y = [
        {"date": str(d.date()) if hasattr(d, 'date') else str(d), "return": round(float(v), 6)}
        for d, v in rolling.items()
        if v == v  # filter NaN
    ]

    return {"returns_series": returns_series, "rolling_1y": rolling_1y}
