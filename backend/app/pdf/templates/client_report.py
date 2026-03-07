from __future__ import annotations
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, HRFlowable

from app.pdf.generator import (
    AdvisorBranding, build_branded_header, build_sebi_disclaimer, build_comparison_table
)

STYLES = getSampleStyleSheet()


def build_client_report(
    branding: AdvisorBranding,
    client_name: str,
    products: list[dict],
    tax_bracket: float,
) -> bytes:
    """
    Build the client presentation PDF.
    Returns PDF bytes. SEBI disclaimer always included.
    No Sharpe ratios or numerical sub-scores in output.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title="Investment Comparison Report",
        author=branding.firm_name,
    )

    elements = []

    # Header
    elements.extend(build_branded_header(branding))

    # Client info
    client_style = ParagraphStyle("client", parent=STYLES["Normal"], fontSize=11)
    elements.append(Paragraph(f"<b>Prepared for:</b> {client_name}", client_style))
    elements.append(Paragraph(
        f"<b>Tax Bracket:</b> {int(tax_bracket*100)}% | "
        f"<b>Date:</b> {date.today().strftime('%d %b %Y')}", client_style
    ))
    elements.append(Spacer(1, 4*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    elements.append(Spacer(1, 4*mm))

    # Title
    elements.append(Paragraph("Investment Comparison Summary", STYLES["Heading2"]))
    elements.append(Spacer(1, 3*mm))

    # Comparison table (client_view=True — no Sharpe/sub-scores)
    elements.append(build_comparison_table(products, client_view=True))
    elements.append(Spacer(1, 6*mm))

    # Note section
    note_style = ParagraphStyle("note", parent=STYLES["Normal"], fontSize=9, textColor=colors.grey)
    elements.append(Paragraph("Returns shown are post-tax estimates. Past performance does not guarantee future results.", note_style))
    elements.append(Spacer(1, 4*mm))

    # Advisor notes area
    elements.append(Paragraph("<b>Advisor Notes:</b>", STYLES["Normal"]))
    elements.append(Spacer(1, 12*mm))  # blank space for handwritten notes
    elements.append(HRFlowable(width="100%", thickness=0.3, color=colors.lightgrey))
    elements.append(Spacer(1, 8*mm))
    elements.append(HRFlowable(width="100%", thickness=0.3, color=colors.lightgrey))
    elements.append(Spacer(1, 4*mm))

    # SEBI disclaimer (always last)
    elements.extend(build_sebi_disclaimer())

    doc.build(elements)
    return buffer.getvalue()
