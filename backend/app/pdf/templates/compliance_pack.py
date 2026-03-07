from __future__ import annotations
import io
import json
import structlog
from datetime import date

logger = structlog.get_logger()

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, HRFlowable
)

from app.pdf.generator import AdvisorBranding, build_branded_header, build_sebi_disclaimer
from app.risk_profiler.questionnaire import QUESTIONS

STYLES = getSampleStyleSheet()


def _get_selected_label(question: dict, selected_value: str) -> str:
    for opt in question.get("options", []):
        if opt["value"] == selected_value:
            return opt["label"]
    return selected_value


def build_compliance_pack(
    branding: AdvisorBranding,
    client_name: str,
    risk_profile,  # RiskProfile ORM object
) -> bytes:
    """
    Build the SEBI compliance pack PDF for a risk profile.
    Contains all Q&A, score, category, advisor rationale, retention date.
    Does NOT contain scoring algorithm weights.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title="Risk Profiling Compliance Pack",
        author=branding.firm_name,
    )

    elements = []

    # Header
    elements.extend(build_branded_header(branding))

    # Title
    elements.append(Paragraph("Risk Profiling Compliance Pack", STYLES["Heading1"]))
    elements.append(Spacer(1, 2*mm))

    # Client + date info
    completed_date = risk_profile.completed_at.strftime("%d %b %Y") if risk_profile.completed_at else date.today().strftime("%d %b %Y")
    retention_date = risk_profile.retention_until.strftime("%d %b %Y") if risk_profile.retention_until else "N/A"

    info_data = [
        ["Client Name:", client_name],
        ["Assessment Date:", completed_date],
        ["Document Retention Until:", retention_date],
        ["Risk Category:", risk_profile.risk_category],
        ["Risk Score:", f"{risk_profile.risk_score:.0f} / 90"],
    ]
    info_table = Table(info_data, colWidths=[50*mm, 100*mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    elements.append(Spacer(1, 4*mm))

    # Q&A section
    elements.append(Paragraph("Questionnaire Responses", STYLES["Heading2"]))
    elements.append(Spacer(1, 3*mm))

    responses = {}
    if risk_profile.question_responses:
        try:
            for r in json.loads(risk_profile.question_responses):
                responses[r["question_id"]] = r.get("selected_value", "")
        except Exception as exc:
            logger.error("compliance_pack_responses_parse_error",
                         risk_profile_id=str(risk_profile.id), error=str(exc))
            # responses stays empty — all answers render as "(No response)"
            # This is a data integrity issue that must be investigated

    q_style = ParagraphStyle("q", parent=STYLES["Normal"], fontSize=9, spaceBefore=4)
    a_style = ParagraphStyle("a", parent=STYLES["Normal"], fontSize=9,
                              textColor=colors.HexColor("#1a56db"), leftIndent=10)

    for i, question in enumerate(QUESTIONS, 1):
        selected = responses.get(question["id"], "")
        label = _get_selected_label(question, selected) if selected else "(No response)"
        elements.append(Paragraph(f"<b>Q{i}. {question['text']}</b>", q_style))
        elements.append(Paragraph(f"Answer: {label}", a_style))

    elements.append(Spacer(1, 6*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    elements.append(Spacer(1, 4*mm))

    # Risk summary
    elements.append(Paragraph("Risk Assessment Summary", STYLES["Heading2"]))
    elements.append(Spacer(1, 2*mm))

    category_style = ParagraphStyle("cat", parent=STYLES["Normal"], fontSize=12,
                                     textColor=colors.HexColor("#1a56db"), fontName="Helvetica-Bold")
    elements.append(Paragraph(f"Risk Category: {risk_profile.risk_category}", category_style))
    elements.append(Spacer(1, 3*mm))

    # Advisor rationale (bordered box)
    elements.append(Paragraph("<b>Advisor Rationale:</b>", STYLES["Normal"]))
    rationale_style = ParagraphStyle("rationale", parent=STYLES["Normal"], fontSize=10,
                                      borderPadding=6, borderColor=colors.grey,
                                      borderWidth=0.5, borderRadius=3, spaceAfter=4)
    elements.append(Paragraph(risk_profile.advisor_rationale, rationale_style))
    elements.append(Spacer(1, 6*mm))

    # Signature lines
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    elements.append(Spacer(1, 4*mm))
    sig_data = [
        ["Advisor Signature: ___________________", "Date: ___________"],
        ["Client Signature:  ___________________", "Date: ___________"],
    ]
    sig_table = Table(sig_data, colWidths=[110*mm, 60*mm])
    sig_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(sig_table)

    # SEBI disclaimer
    elements.extend(build_sebi_disclaimer())

    doc.build(elements)
    return buffer.getvalue()
