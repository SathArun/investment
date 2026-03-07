from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_advisor
from app.clients.service import create_client, get_clients, get_client, update_client, VALID_TAX_BRACKETS
from app.db.base import get_db

router = APIRouter(prefix="/api/clients", tags=["clients"])


class ClientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    tax_bracket: Optional[float] = None
    risk_category: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    tax_bracket: Optional[float] = None
    risk_category: Optional[str] = None


def _to_dict(client):
    return {
        "id": client.id,
        "advisor_id": client.advisor_id,
        "name": client.name,
        "age": client.age,
        "tax_bracket": client.tax_bracket,
        "risk_category": client.risk_category,
        "created_at": client.created_at.isoformat() if client.created_at else None,
        "updated_at": client.updated_at.isoformat() if client.updated_at else None,
    }


@router.get("")
def list_clients(
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    return [_to_dict(c) for c in get_clients(db, advisor_id)]


@router.post("", status_code=201)
def create(
    body: ClientCreate,
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    try:
        client = create_client(db, advisor_id, body.name, body.age, body.tax_bracket, body.risk_category)
        return _to_dict(client)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{client_id}")
def get_one(
    client_id: str,
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    client = get_client(db, advisor_id, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return _to_dict(client)


@router.patch("/{client_id}")
def update(
    client_id: str,
    body: ClientUpdate,
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    try:
        client = update_client(db, advisor_id, client_id, **body.model_dump(exclude_none=True))
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return _to_dict(client)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
