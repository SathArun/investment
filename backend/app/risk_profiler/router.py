"""FastAPI router for SEBI risk profiler endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_advisor
from app.db.base import get_db
from app.goals.models import Client
from app.risk_profiler.questionnaire import get_questions
from app.risk_profiler.service import create_risk_profile, get_risk_description

router = APIRouter(prefix="/api", tags=["risk-profiler"])


class QuestionResponse(BaseModel):
    question_id: str
    selected_value: str


class RiskProfileRequest(BaseModel):
    client_id: str
    responses: list[QuestionResponse]
    advisor_rationale: str

    @field_validator("responses")
    @classmethod
    def responses_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("At least one questionnaire response is required")
        return v

    @field_validator("advisor_rationale")
    @classmethod
    def rationale_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("advisor_rationale is required for SEBI compliance")
        return v


@router.get("/risk-profiler/questions")
def get_risk_questions():
    """Return the full 18-question SEBI risk profiler questionnaire."""
    return get_questions()


@router.post("/risk-profiles", status_code=201)
def create_profile(
    body: RiskProfileRequest,
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    """
    Submit completed risk profiler responses for a client.

    Validates that the client belongs to the authenticated advisor,
    computes the risk score, assigns a SEBI risk category, and
    persists the profile with the advisor's rationale.
    """
    client = (
        db.query(Client)
        .filter(Client.id == body.client_id, Client.advisor_id == advisor_id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    responses = [r.model_dump() for r in body.responses]
    profile = create_risk_profile(
        db,
        advisor_id,
        body.client_id,
        responses,
        body.advisor_rationale,
    )

    return {
        "id": profile.id,
        "risk_score": profile.risk_score,
        "risk_category": profile.risk_category,
        "risk_description": get_risk_description(profile.risk_category),
        "retention_until": (
            profile.retention_until.isoformat() if profile.retention_until else None
        ),
    }
