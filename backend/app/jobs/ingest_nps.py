"""NPSTRUST NPS fund returns ingestion (weekly scrape)."""
from __future__ import annotations
import re
from datetime import date, datetime
from typing import Optional

import structlog
from bs4 import BeautifulSoup

from app.db.base import SessionLocal
from app.market_data.models import IndexHistory

logger = structlog.get_logger()

# PFM name normalization map
PFM_NAMES = {
    "SBI Pension Funds": "SBI",
    "LIC Pension Fund": "LIC",
    "UTI Retirement Solutions": "UTI",
    "HDFC Pension Management": "HDFC",
    "ICICI Prudential Pension": "ICICI",
    "Kotak Mahindra Pension": "KOTAK",
    "Aditya Birla Sun Life Pension": "ABSL",
    "Tata Pension Management": "TATA",
    "Max Life Pension Fund": "MAXLIFE",
}

SCHEME_TYPES = {
    "Equity": "EQUITY",
    "Government Bonds": "GBOND",
    "G-Bond": "GBOND",
    "Corporate Bonds": "CORPBOND",
    "Corp-Bond": "CORPBOND",
    "Alternative Assets": "ALTERNATE",
    "Alternate": "ALTERNATE",
}

RETURN_HORIZONS = ["1Y", "3Y", "5Y"]


def make_nps_ticker(pfm_short: str, scheme_short: str, horizon: str) -> str:
    """Generate NPS synthetic ticker: NPS_{PFM}_{SCHEME}_{HORIZON}"""
    return f"NPS_{pfm_short}_{scheme_short}_{horizon}"


def _match_pfm(text: str) -> Optional[str]:
    """Return PFM short code if text contains a known PFM name."""
    text_lower = text.lower()
    for full_name, short in PFM_NAMES.items():
        if full_name.lower() in text_lower:
            return short
    return None


def _match_scheme(text: str) -> Optional[str]:
    """Return scheme short code if text contains a known scheme type."""
    text_lower = text.lower()
    for full_type, short_type in SCHEME_TYPES.items():
        if full_type.lower() in text_lower:
            return short_type
    return None


def _extract_return_pct(cell_text: str) -> Optional[float]:
    """
    Extract a percentage return value from a cell string.
    Returns decimal (e.g. 0.1552 for 15.52%) or None if not a valid return.
    Rejects values outside the plausible -50% to +100% annual return range.
    """
    cleaned = re.sub(r"[%,\s]", "", cell_text)
    if not cleaned or cleaned in ("-", "N/A", "NA", "--"):
        return None
    try:
        val = float(cleaned)
        # Returns should be in percent display (e.g. 15.52), not already decimal
        if -50.0 <= val <= 100.0:
            return round(val / 100.0, 6)
    except ValueError:
        pass
    return None


def parse_nps_html(html: str, as_of_date: Optional[date] = None) -> list[dict]:
    """
    Parse NPSTRUST HTML table into list of records.
    Returns records with: ticker, price_date, close_price (as return value in decimal).

    Handles two common table layouts:
    1. Each row has PFM name + scheme type in the first two cells.
    2. PFM name spans multiple rows (rowspan); scheme type is the only identifier per row.
    """
    if as_of_date is None:
        as_of_date = date.today()

    records = []
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    logger.info("nps_parse_tables_found", table_count=len(tables), html_length=len(html))

    for t_idx, table in enumerate(tables):
        rows = table.find_all("tr")
        current_pfm: Optional[str] = None  # carry PFM forward across rowspan rows

        for row in rows:
            cells = [td.get_text(separator=" ", strip=True) for td in row.find_all(["td", "th"])]
            if not cells:
                continue

            # Scan all cells for PFM and scheme identifiers
            pfm_short: Optional[str] = None
            scheme_short: Optional[str] = None

            for cell in cells:
                if pfm_short is None:
                    pfm_short = _match_pfm(cell)
                if scheme_short is None:
                    scheme_short = _match_scheme(cell)

            # Carry PFM forward if this row only has scheme info (rowspan layout)
            if pfm_short:
                current_pfm = pfm_short
            elif current_pfm:
                pfm_short = current_pfm

            if not pfm_short or not scheme_short:
                continue

            # Collect plausible return values from all cells
            return_values = [_extract_return_pct(c) for c in cells]
            valid_returns = [v for v in return_values if v is not None]

            if len(valid_returns) < len(RETURN_HORIZONS):
                logger.debug(
                    "nps_row_insufficient_returns",
                    pfm=pfm_short, scheme=scheme_short,
                    found=len(valid_returns), need=len(RETURN_HORIZONS),
                )
                continue

            for i, horizon in enumerate(RETURN_HORIZONS):
                records.append({
                    "ticker": make_nps_ticker(pfm_short, scheme_short, horizon),
                    "price_date": as_of_date,
                    "close_price": valid_returns[i],
                })

        logger.info("nps_table_parsed", table_index=t_idx, records_so_far=len(records))

    return records


def upsert_nps_returns(records: list[dict], session) -> tuple[int, int]:
    """Upsert NPS return records. On conflict (same ticker+date), update the value."""
    inserted = 0
    updated = 0
    for record in records:
        existing = session.get(IndexHistory, (record["ticker"], record["price_date"]))
        if existing is not None:
            existing.close_price = record["close_price"]
            updated += 1
        else:
            row = IndexHistory(
                ticker=record["ticker"],
                price_date=record["price_date"],
                close_price=record["close_price"],
            )
            session.add(row)
            inserted += 1
    session.commit()
    return inserted, updated


def fetch_nps_html() -> str:
    """Fetch NPSTRUST returns HTML page."""
    import requests
    url = "https://www.npstrust.org.in/content/performance-nps-scheme"
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.error("nps_fetch_error", error=str(e))
        raise


def run() -> int:
    """Main entry point for NPS returns ingestion. Returns total rows processed."""
    logger.info("nps_job_start")
    try:
        html = fetch_nps_html()
        records = parse_nps_html(html)
        logger.info("nps_parsed", record_count=len(records))

        with SessionLocal() as session:
            inserted, updated = upsert_nps_returns(records, session)
            logger.info("nps_job_complete", inserted=inserted, updated=updated)
        return inserted + updated
    except Exception as e:
        logger.error("nps_job_failed", error=str(e))
        # Don't re-raise — retain previous week's data
        logger.info("nps_job_fallback", message="Retaining previous data")
        return 0


if __name__ == "__main__":
    run()
