from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_advisor
from app.db.base import get_db
from app.market_data.service import get_products, get_product_history

router = APIRouter(prefix="/api/products", tags=["market-data"])


@router.get("")
def list_products(
    tax_bracket: float = 0.30,
    time_horizon: str = "long",
    risk_filter: Optional[str] = None,
    sort_by: str = "score_total",
    sort_dir: str = "desc",
    db: Session = Depends(get_db),
    _advisor_id: str = Depends(get_current_advisor),
):
    return get_products(db, tax_bracket, time_horizon, risk_filter, sort_by, sort_dir)


@router.get("/{product_id}/history")
def product_history(
    product_id: str,
    period: str = "5y",
    db: Session = Depends(get_db),
    _advisor_id: str = Depends(get_current_advisor),
):
    result = get_product_history(db, product_id, period)
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return result
