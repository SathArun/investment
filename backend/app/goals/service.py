from __future__ import annotations
import uuid
from datetime import date, datetime, timezone
from typing import Optional
import math

import structlog

from app.goals.models import Goal, Client

logger = structlog.get_logger()

RETURN_SCENARIOS = {"conservative": 0.08, "base": 0.12, "optimistic": 0.16}

ALLOCATION_RULES = {
    "short": [  # 0-3Y
        {"name": "Liquid Fund", "asset_class": "debt_liquid", "pct": 40},
        {"name": "Corporate Bond", "asset_class": "debt_corporate", "pct": 40},
        {"name": "Gold ETF", "asset_class": "gold_etf", "pct": 20},
    ],
    "medium": [  # 3-7Y
        {"name": "Balanced Hybrid", "asset_class": "eq_balanced", "pct": 40},
        {"name": "Short Duration Debt", "asset_class": "debt_shortterm", "pct": 30},
        {"name": "Gold ETF", "asset_class": "gold_etf", "pct": 20},
        {"name": "REIT", "asset_class": "reit", "pct": 10},
    ],
    "long": [  # 7Y+
        {"name": "Large Cap Equity", "asset_class": "eq_largecap", "pct": 50},
        {"name": "Mid Cap Equity", "asset_class": "eq_midcap", "pct": 20},
        {"name": "NPS Tier 1", "asset_class": "nps", "pct": 15},
        {"name": "Gold ETF", "asset_class": "gold_etf", "pct": 10},
        {"name": "REIT", "asset_class": "reit", "pct": 5},
    ],
}


def _fv_lumpsum(pv: float, rate: float, years: float) -> float:
    """Future value of lumpsum at annual rate over years."""
    return pv * (1 + rate) ** years


def _fv_sip_with_stepup(monthly_sip: float, annual_return: float, years: int, annual_stepup_pct: float) -> float:
    """
    Future value of SIP with annual step-up.
    Each year the SIP increases by annual_stepup_pct.
    """
    monthly_rate = (1 + annual_return) ** (1/12) - 1
    total_fv = 0.0
    current_sip = monthly_sip
    for year in range(years):
        # FV of this year's SIPs at end of total period
        months_remaining = (years - year) * 12
        if monthly_rate == 0:
            year_fv = current_sip * months_remaining
        else:
            year_fv = current_sip * ((1 + monthly_rate) ** months_remaining - 1) / monthly_rate
        total_fv += year_fv
        current_sip *= (1 + annual_stepup_pct)
    return total_fv


def _required_sip(gap: float, annual_return: float, years: int) -> float:
    """Monthly SIP needed to accumulate gap over years at annual_return."""
    if gap <= 0:
        return 0.0
    monthly_rate = (1 + annual_return) ** (1/12) - 1
    if monthly_rate == 0:
        return gap / (years * 12)
    n = years * 12
    return gap * monthly_rate / ((1 + monthly_rate) ** n - 1)


def compute_goal_plan(goal: Goal, client: Client) -> dict:
    today = date.today()
    if goal.target_date:
        years = max(1, (goal.target_date - today).days // 365)
    else:
        years = 10  # default

    inflation_rate = goal.inflation_rate or 0.06
    target_amount = goal.target_amount_inr or 0
    current_corpus = goal.current_corpus_inr or 0
    monthly_sip = goal.monthly_sip_inr or 0
    stepup = goal.annual_stepup_pct or 0.0
    base_return = RETURN_SCENARIOS["base"]

    # 1. Inflation-adjusted target
    inflation_adjusted_target = target_amount * (1 + inflation_rate) ** years

    # 2. Future value of current corpus
    corpus_fv = _fv_lumpsum(current_corpus, base_return, years)

    # 3. Future value of SIPs with step-up
    sip_fv = _fv_sip_with_stepup(monthly_sip, base_return, years, stepup)

    corpus_at_trajectory = corpus_fv + sip_fv
    gap = max(0, inflation_adjusted_target - corpus_at_trajectory)
    required_sip = _required_sip(gap, base_return, years)

    # 4. Goal probability (simplified: based on years and gap ratio)
    if gap <= 0:
        goal_probability = 0.90
    elif gap / inflation_adjusted_target < 0.1:
        goal_probability = 0.75
    elif gap / inflation_adjusted_target < 0.3:
        goal_probability = 0.55
    else:
        goal_probability = 0.35

    # 5. Allocation based on horizon
    if years <= 3:
        horizon_key = "short"
    elif years <= 7:
        horizon_key = "medium"
    else:
        horizon_key = "long"
    recommended_allocation = ALLOCATION_RULES[horizon_key]

    # 6. NPS highlight: long-term + high tax bracket
    tax_bracket = client.tax_bracket or 0.0
    nps_highlight = years >= 10 and tax_bracket >= 0.20

    # 7. Corpus projection at 3 scenarios
    corpus_projection = []
    for year in range(1, years + 1):
        row = {"year": today.year + year}
        for scenario, rate in RETURN_SCENARIOS.items():
            c_fv = _fv_lumpsum(current_corpus, rate, year)
            s_fv = _fv_sip_with_stepup(monthly_sip, rate, year, stepup)
            row[scenario] = round(c_fv + s_fv, 2)
        corpus_projection.append(row)

    return {
        "inflation_adjusted_target": round(inflation_adjusted_target, 2),
        "corpus_at_current_trajectory": round(corpus_at_trajectory, 2),
        "gap_amount": round(gap, 2),
        "required_sip": round(required_sip, 2),
        "goal_probability": round(goal_probability, 2),
        "nps_highlight": nps_highlight,
        "recommended_allocation": recommended_allocation,
        "corpus_projection": corpus_projection,
    }


def create_goal(session, advisor_id: str, client_id: str, name: str, **kwargs) -> Goal:
    goal = Goal(
        id=str(uuid.uuid4()),
        client_id=client_id,
        advisor_id=advisor_id,
        name=name,
        created_at=datetime.now(timezone.utc),
        **{k: v for k, v in kwargs.items() if v is not None},
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


def get_goal(session, advisor_id: str, goal_id: str) -> Optional[Goal]:
    return session.query(Goal).filter(Goal.id == goal_id, Goal.advisor_id == advisor_id).first()
