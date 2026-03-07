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


def parse_nps_html(html: str, as_of_date: Optional[date] = None) -> list[dict]:
    """
    Parse NPSTRUST HTML table into list of records.
    Returns records with: ticker, price_date, close_price (as return value in decimal).
    Missing/NA values stored as None (skipped).
    """
    if as_of_date is None:
        as_of_date = date.today()

    records = []
    soup = BeautifulSoup(html, "html.parser")

    # Find all tables or rows with return data
    # The NPSTRUST format typically has a table with PFM name, scheme type, and returns
    tables = soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) < 5:
                continue

            # Try to identify PFM name and scheme type from cells
            pfm_short = None
            scheme_short = None

            for cell in cells[:3]:
                for full_name, short in PFM_NAMES.items():
                    if full_name.lower() in cell.lower() or short.lower() in cell.lower():
                        pfm_short = short
                        break
                for full_type, short_type in SCHEME_TYPES.items():
                    if full_type.lower() in cell.lower():
                        scheme_short = short_type
                        break

            if not pfm_short or not scheme_short:
                continue

            # Extract return values (last 3-5 numeric cells)
            return_values = []
            for cell in cells:
                cleaned = cell.replace('%', '').replace(',', '').strip()
                try:
                    val = float(cleaned)
                    return_values.append(val / 100.0)  # Convert to decimal
                except ValueError:
                    return_values.append(None)

            # Map to 1Y, 3Y, 5Y
            valid_returns = [v for v in return_values if v is not None]
            for i, horizon in enumerate(RETURN_HORIZONS):
                if i < len(valid_returns):
                    ticker = make_nps_ticker(pfm_short, scheme_short, horizon)
                    records.append({
                        "ticker": ticker,
                        "price_date": as_of_date,
                        "close_price": valid_returns[i],
                    })

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


def run() -> None:
    """Main entry point for NPS returns ingestion."""
    logger.info("nps_job_start")
    try:
        html = fetch_nps_html()
        records = parse_nps_html(html)
        logger.info("nps_parsed", record_count=len(records))

        with SessionLocal() as session:
            inserted, updated = upsert_nps_returns(records, session)
            logger.info("nps_job_complete", inserted=inserted, updated=updated)
    except Exception as e:
        logger.error("nps_job_failed", error=str(e))
        # Don't re-raise — retain previous week's data
        logger.info("nps_job_fallback", message="Retaining previous data")


if __name__ == "__main__":
    run()
