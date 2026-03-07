"""Unit tests for SEBI risk profiler questionnaire and scoring logic."""
from __future__ import annotations

import pytest

from app.risk_profiler.questionnaire import QUESTIONS, get_questions
from app.risk_profiler.service import (
    RISK_DESCRIPTIONS,
    assign_risk_category,
    compute_risk_score,
    get_risk_description,
)

REQUIRED_CATEGORIES = {"age", "income", "assets", "objective", "horizon", "behavioral", "liquidity"}


def _responses_for_score(target_score: int) -> list[dict]:
    """Build a response list by selecting the option with score == target_score for every question."""
    responses = []
    for q in QUESTIONS:
        chosen = next(
            (opt for opt in q["options"] if opt["score"] == target_score),
            None,
        )
        # Fall back to the option closest to target_score if exact match not found
        if chosen is None:
            chosen = min(q["options"], key=lambda o: abs(o["score"] - target_score))
        responses.append({"question_id": q["id"], "selected_value": chosen["value"]})
    return responses


def test_get_questions_returns_18():
    """The questionnaire must contain exactly 18 questions."""
    assert len(get_questions()) == 18


def test_all_categories_covered():
    """Every required SEBI dimension must appear at least once."""
    categories = {q["category"] for q in get_questions()}
    assert REQUIRED_CATEGORIES.issubset(categories)


def test_conservative_score():
    """Selecting the lowest-scoring option for every question must yield the Conservative category."""
    responses = _responses_for_score(1)
    score = compute_risk_score(responses)
    category = assign_risk_category(score)
    assert category == "Conservative", f"Expected Conservative, got {category} (score={score})"


def test_aggressive_score():
    """Selecting the highest-scoring option for every question must yield the Aggressive category."""
    responses = _responses_for_score(5)
    score = compute_risk_score(responses)
    category = assign_risk_category(score)
    assert category == "Aggressive", f"Expected Aggressive, got {category} (score={score})"


def test_moderate_score():
    """A mix of answers should map to one of the five valid categories."""
    valid_categories = {
        "Conservative",
        "Moderately Conservative",
        "Moderate",
        "Moderately Aggressive",
        "Aggressive",
    }
    # Build a mixed response by alternating score 2 and score 4
    responses = []
    for i, q in enumerate(QUESTIONS):
        target = 4 if i % 2 == 0 else 2
        chosen = next(
            (opt for opt in q["options"] if opt["score"] == target),
            q["options"][0],
        )
        responses.append({"question_id": q["id"], "selected_value": chosen["value"]})

    score = compute_risk_score(responses)
    category = assign_risk_category(score)
    assert category in valid_categories


def test_risk_description_not_empty():
    """Every risk category must have a non-empty description."""
    for category in ["Conservative", "Moderately Conservative", "Moderate", "Moderately Aggressive", "Aggressive"]:
        desc = get_risk_description(category)
        assert desc, f"Description for '{category}' is empty"


def test_score_boundary_conservative():
    """A score of exactly 36 must be categorised as Conservative."""
    assert assign_risk_category(36) == "Conservative"


def test_score_boundary_moderately_conservative():
    """A score of exactly 37 must be categorised as Moderately Conservative."""
    assert assign_risk_category(37) == "Moderately Conservative"
