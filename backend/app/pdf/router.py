from __future__ import annotations
import re as _re
from datetime import date
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_advisor
from app.db.base import get_db
from app.pdf.generator import AdvisorBranding, ensure_pdf_dir

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

WHATSAPP_BASE = "https://wa.me/?text="

_UUID_RE = _re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', _re.IGNORECASE)

def _safe_filename_part(value: str) -> str:
    """Strip any chars that aren't alphanumeric, hyphen, or underscore."""
    return _re.sub(r'[^a-zA-Z0-9\-_]', '_', str(value))


class ClientReportRequest(BaseModel):
    client_id: str
    product_ids: list[str]
    tax_bracket: float = Field(default=0.30, ge=0.0, le=1.0)
    time_horizon: Literal["short", "medium", "long"] = "long"


class CompliancePackRequest(BaseModel):
    risk_profile_id: str


@router.post("/client-report")
def generate_client_report(
    body: ClientReportRequest,
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    from app.auth.models import Advisor
    from app.goals.models import Client
    from app.analytics.models import AdvisorScore, ComputedMetric
    from app.market_data.models import AssetClass, MutualFund
    from app.pdf.templates.client_report import build_client_report

    if len(body.product_ids) > 5:
        raise HTTPException(status_code=422, detail="Maximum 5 products allowed per report")
    if not body.product_ids:
        raise HTTPException(status_code=422, detail="At least 1 product_id required")

    advisor = db.get(Advisor, advisor_id)
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")

    client = db.query(Client).filter(Client.id == body.client_id, Client.advisor_id == advisor_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Fetch product data
    products = []
    for pid in body.product_ids:
        score = db.query(AdvisorScore).filter(
            AdvisorScore.product_id == pid,
            AdvisorScore.tax_bracket == body.tax_bracket,
            AdvisorScore.time_horizon == body.time_horizon,
        ).order_by(AdvisorScore.computed_date.desc()).first()

        cm = db.query(ComputedMetric).filter(
            ComputedMetric.product_id == pid,
        ).order_by(ComputedMetric.computed_date.desc()).first()

        # Try to get name from asset class or mutual fund
        ac = db.get(AssetClass, pid)
        mf = db.get(MutualFund, pid)
        name = (mf.scheme_name if mf else None) or (ac.name if ac else pid)
        sebi_risk_label = None
        if ac:
            labels = {1: "Low", 2: "Low to Moderate", 3: "Moderate", 4: "Moderately High", 5: "High", 6: "Very High"}
            sebi_risk_label = labels.get(ac.sebi_risk_level)

        products.append({
            "id": pid,
            "name": name,
            "sebi_risk_label": sebi_risk_label or "Unknown",
            "cagr_1y": cm.cagr_1y if cm else None,
            "cagr_3y": cm.cagr_3y if cm else None,
            "cagr_5y": cm.cagr_5y if cm else None,
            "post_tax_return_3y": score.post_tax_return_3y if score else None,
            "advisor_score": score.score_total if score else None,
            "sharpe_3y": cm.sharpe_3y if cm else None,
        })

    branding = AdvisorBranding.from_advisor(advisor)
    pdf_bytes = build_client_report(branding, client.name, products, body.tax_bracket)

    # Save to disk
    if not _UUID_RE.match(advisor_id):
        raise HTTPException(status_code=400, detail="Invalid advisor ID format")
    pdf_dir = ensure_pdf_dir(advisor_id)
    safe_client_id = _safe_filename_part(client.id)
    filename = f"client_report_{safe_client_id}_{date.today().isoformat()}.pdf"
    (pdf_dir / filename).write_bytes(pdf_bytes)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/compliance-pack")
def generate_compliance_pack(
    body: CompliancePackRequest,
    db: Session = Depends(get_db),
    advisor_id: str = Depends(get_current_advisor),
):
    from app.auth.models import Advisor
    from app.goals.models import Client
    from app.risk_profiler.models import RiskProfile
    from app.pdf.templates.compliance_pack import build_compliance_pack

    advisor = db.get(Advisor, advisor_id)
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")

    profile = db.query(RiskProfile).filter(
        RiskProfile.id == body.risk_profile_id,
        RiskProfile.advisor_id == advisor_id,
        RiskProfile.is_deleted == False,
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Risk profile not found")

    if not profile.advisor_rationale or not profile.advisor_rationale.strip():
        raise HTTPException(status_code=422, detail="Advisor rationale is required for compliance pack generation")

    client = db.get(Client, profile.client_id)
    if not client:
        raise HTTPException(status_code=422, detail="Client associated with this risk profile no longer exists")
    client_name = client.name

    branding = AdvisorBranding.from_advisor(advisor)
    pdf_bytes = build_compliance_pack(branding, client_name, profile)

    # Save to disk and update DB
    if not _UUID_RE.match(advisor_id):
        raise HTTPException(status_code=400, detail="Invalid advisor ID format")
    pdf_dir = ensure_pdf_dir(advisor_id)
    safe_profile_id = _safe_filename_part(profile.id)
    filename = f"compliance_{safe_profile_id}_{date.today().isoformat()}.pdf"
    pdf_path = pdf_dir / filename
    pdf_path.write_bytes(pdf_bytes)

    profile.compliance_pdf_path = str(pdf_path)
    db.commit()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
