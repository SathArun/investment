from __future__ import annotations
import io
import os
import uuid as _uuid
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable, Image, Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate
)

SEBI_DISCLAIMER = (
    "Investment in securities market are subject to market risks. "
    "Read all the related documents carefully before investing."
)

PDF_DIR = Path(__file__).parent.parent.parent / "data" / "pdfs"
STYLES = getSampleStyleSheet()


@dataclass
class AdvisorBranding:
    advisor_id: str
    firm_name: str
    name: str
    contact_phone: Optional[str] = None
    logo_path: Optional[str] = None
    primary_color: Optional[str] = None

    @classmethod
    def from_advisor(cls, advisor) -> "AdvisorBranding":
        return cls(
            advisor_id=advisor.id,
            firm_name=advisor.firm_name or advisor.name,
            name=advisor.name,
            contact_phone=advisor.contact_phone,
            logo_path=advisor.logo_path,
            primary_color=advisor.primary_color or "#1a56db",
        )


def build_branded_header(branding: AdvisorBranding) -> list:
    """Returns list of Flowables for the branded header."""
    elements = []
    header_style = ParagraphStyle(
        "header", parent=STYLES["Heading1"],
        fontSize=16, textColor=colors.HexColor(branding.primary_color or "#1a56db"),
    )
    sub_style = ParagraphStyle("sub", parent=STYLES["Normal"], fontSize=10, textColor=colors.grey)

    # Logo
    if branding.logo_path and os.path.exists(branding.logo_path):
        try:
            elements.append(Image(branding.logo_path, width=60*mm, height=15*mm))
        except Exception:
            pass  # Logo load failure is non-fatal

    elements.append(Paragraph(branding.firm_name, header_style))
    if branding.contact_phone:
        elements.append(Paragraph(f"Contact: {branding.contact_phone}", sub_style))
    elements.append(Paragraph(f"Report Date: {date.today().strftime('%d %b %Y')}", sub_style))
    elements.append(Spacer(1, 6*mm))
    return elements


def build_sebi_disclaimer() -> list:
    """Returns Flowables for the SEBI disclaimer. ALWAYS included."""
    disclaimer_style = ParagraphStyle(
        "disclaimer", parent=STYLES["Normal"],
        fontSize=8, textColor=colors.grey,
        borderPadding=4, borderColor=colors.grey,
        borderWidth=0.5, borderRadius=2,
    )
    return [
        Spacer(1, 4*mm),
        Paragraph(f"<b>Disclaimer:</b> {SEBI_DISCLAIMER}", disclaimer_style),
    ]


def build_comparison_table(products: list[dict], client_view: bool = True) -> Table:
    """
    Build a comparison table for products.
    client_view=True: omit Sharpe ratios, sub-scores, numerical scores.
    Columns (client_view): Product Name | Risk | 1Y Return | 3Y Return | 5Y Return | Min Investment
    """
    def fmt_pct(v):
        return f"{v*100:.1f}%" if v is not None else "N/A"

    if client_view:
        headers = ["Product", "Risk Level", "1Y Return", "3Y Return", "5Y Return"]
        rows = [headers]
        for p in products:
            rows.append([
                p.get("name", p.get("id", "Unknown")),
                p.get("sebi_risk_label", "Unknown"),
                fmt_pct(p.get("cagr_1y")),
                fmt_pct(p.get("cagr_3y")),
                fmt_pct(p.get("cagr_5y")),
            ])
    else:
        headers = ["Product", "Risk", "Advisor Score", "1Y", "3Y", "5Y", "Sharpe (3Y)"]
        rows = [headers]
        for p in products:
            rows.append([
                p.get("name", p.get("id", "Unknown")),
                p.get("sebi_risk_label", "Unknown"),
                f"{p.get('advisor_score', 0):.1f}",
                fmt_pct(p.get("cagr_1y")),
                fmt_pct(p.get("cagr_3y")),
                fmt_pct(p.get("cagr_5y")),
                f"{p.get('sharpe_3y', 0):.2f}" if p.get("sharpe_3y") else "N/A",
            ])

    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a56db")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8ff")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def ensure_pdf_dir(advisor_id: str) -> Path:
    # Validate UUID format to prevent path traversal via advisor_id
    try:
        safe_id = str(_uuid.UUID(advisor_id))
    except ValueError:
        raise ValueError(f"Invalid advisor_id format: {advisor_id!r}")
    pdf_dir = PDF_DIR / safe_id
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return pdf_dir
