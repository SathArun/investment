"""Business logic for SEBI risk profiler scoring and persistence."""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import structlog
from sqlalchemy.orm import Session

from app.risk_profiler.models import RiskProfile
from app.risk_profiler.questionnaire import QUESTIONS

logger = structlog.get_logger()

# Score thresholds (out of max possible score = 18 questions × 5 = 90)
RISK_THRESHOLDS = [
    (36, "Conservative"),
    (54, "Moderately Conservative"),
    (63, "Moderate"),
    (72, "Moderately Aggressive"),
    (float("inf"), "Aggressive"),
]

RISK_DESCRIPTIONS = {
    "Conservative": (
        "You prefer capital preservation over growth. Suitable products: Fixed Deposits, "
        "PPF, Liquid Funds, Government Securities. Expected volatility: Very Low."
    ),
    "Moderately Conservative": (
        "You accept minimal risk for slightly better returns. Suitable: Debt Mutual Funds, "
        "Short Duration Funds, Conservative Hybrid Funds. Expected volatility: Low."
    ),
    "Moderate": (
        "You seek balanced growth with moderate risk. Suitable: Balanced Advantage Funds, "
        "Multi-Asset Funds, NPS. Expected volatility: Moderate."
    ),
    "Moderately Aggressive": (
        "You accept higher volatility for better long-term returns. Suitable: Large Cap Funds, "
        "Flexi Cap Funds, REIT. Expected volatility: High."
    ),
    "Aggressive": (
        "You seek maximum long-term growth and can withstand significant drawdowns. "
        "Suitable: Mid/Small Cap Funds, Sector Funds, International Equity. Expected volatility: Very High."
    ),
}


def compute_risk_score(responses: list[dict]) -> float:
    """
    Compute total risk score from questionnaire responses.

    responses: list of {question_id: str, selected_value: str}
    Returns total score (sum of selected option scores).
    """
    question_map = {q["id"]: q for q in QUESTIONS}
    total = 0
    for response in responses:
        q_id = response.get("question_id")
        selected = response.get("selected_value")
        question = question_map.get(q_id)
        if not question:
            continue
        for option in question["options"]:
            if option["value"] == selected:
                total += option["score"]
                break
    return float(total)


def assign_risk_category(score: float) -> str:
    """Map a numeric score to a SEBI risk category label."""
    for threshold, category in RISK_THRESHOLDS:
        if score <= threshold:
            return category
    return "Aggressive"


def get_risk_description(category: str) -> str:
    """Return the plain-text description for a given risk category."""
    return RISK_DESCRIPTIONS.get(category, "")


def create_risk_profile(
    session: Session,
    advisor_id: str,
    client_id: str,
    responses: list[dict],
    advisor_rationale: str,
) -> RiskProfile:
    """Persist a new RiskProfile record and return it."""
    score = compute_risk_score(responses)
    category = assign_risk_category(score)
    now = datetime.now(timezone.utc)
    retention = date.today() + timedelta(days=5 * 365)

    profile = RiskProfile(
        id=str(uuid.uuid4()),
        client_id=client_id,
        advisor_id=advisor_id,
        completed_at=now,
        risk_score=score,
        risk_category=category,
        question_responses=json.dumps(responses),
        advisor_rationale=advisor_rationale,
        retention_until=retention,
        is_deleted=False,
        created_at=now,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    logger.info(
        "risk_profile_created",
        profile_id=profile.id,
        client_id=client_id,
        score=score,
        category=category,
    )
    return profile
