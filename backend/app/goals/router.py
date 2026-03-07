from __future__ import annotations
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_advisor
from app.db.base import get_db
from app.goals.service import create_goal, get_goal, compute_goal_plan
from app.goals.models import Client

router = APIRouter(prefix="/api/goals", tags=["goals"])


class GoalCreate(BaseModel):
    client_id: str
    name: str
    target_amount_inr: Optional[float] = Field(default=None, ge=0)
    target_date: Optional[date] = None
    current_corpus_inr: Optional[float] = Field(default=0.0, ge=0)
    monthly_sip_inr: Optional[float] = Field(default=0.0, ge=0)
    annual_stepup_pct: Optional[float] = Field(default=0.0, ge=0, le=1.0)
    inflation_rate: Optional[float] = Field(default=0.06, ge=0, le=0.5)


@router.post("", status_code=201)
def create(
    body: GoalCreate,
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    # Verify client belongs to this advisor
    client = db.query(Client).filter(Client.id == body.client_id, Client.advisor_id == advisor_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    goal = create_goal(db, advisor_id, body.client_id, body.name,
                       target_amount_inr=body.target_amount_inr,
                       target_date=body.target_date,
                       current_corpus_inr=body.current_corpus_inr,
                       monthly_sip_inr=body.monthly_sip_inr,
                       annual_stepup_pct=body.annual_stepup_pct,
                       inflation_rate=body.inflation_rate)
    return {"id": goal.id, "name": goal.name, "client_id": goal.client_id}


@router.get("/{goal_id}/plan")
def get_plan(
    goal_id: str,
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    goal = get_goal(db, advisor_id, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    client = db.get(Client, goal.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return compute_goal_plan(goal, client)
