from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.goals.models import Client

VALID_TAX_BRACKETS = {0.0, 0.05, 0.10, 0.20, 0.30}
VALID_RISK_CATEGORIES = {"Conservative", "Moderately Conservative", "Moderate", "Moderately Aggressive", "Aggressive"}


def create_client(session: Session, advisor_id: str, name: str, age: Optional[int] = None,
                  tax_bracket: Optional[float] = None, risk_category: Optional[str] = None) -> Client:
    if tax_bracket is not None and tax_bracket not in VALID_TAX_BRACKETS:
        raise ValueError(f"Invalid tax_bracket: {tax_bracket}. Must be one of {sorted(VALID_TAX_BRACKETS)}")
    if risk_category is not None and risk_category not in VALID_RISK_CATEGORIES:
        raise ValueError(f"Invalid risk_category: {risk_category}")
    client = Client(
        id=str(uuid.uuid4()),
        advisor_id=advisor_id,
        name=name,
        age=age,
        tax_bracket=tax_bracket,
        risk_category=risk_category,
        created_at=datetime.now(timezone.utc),
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


def get_clients(session: Session, advisor_id: str) -> list[Client]:
    return session.query(Client).filter(Client.advisor_id == advisor_id).order_by(Client.created_at).all()


def get_client(session: Session, advisor_id: str, client_id: str) -> Optional[Client]:
    """Returns None if not found OR belongs to different advisor (no information disclosure)."""
    return session.query(Client).filter(
        Client.id == client_id,
        Client.advisor_id == advisor_id,
    ).first()


def update_client(session: Session, advisor_id: str, client_id: str, **updates) -> Optional[Client]:
    client = get_client(session, advisor_id, client_id)
    if not client:
        return None
    if "tax_bracket" in updates and updates["tax_bracket"] not in VALID_TAX_BRACKETS:
        raise ValueError(f"Invalid tax_bracket")
    if "risk_category" in updates and updates["risk_category"] not in VALID_RISK_CATEGORIES:
        raise ValueError(f"Invalid risk_category")
    for k, v in updates.items():
        if v is not None:
            setattr(client, k, v)
    client.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(client)
    return client
