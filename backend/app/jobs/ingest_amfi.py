"""AMFI daily NAV ingestion job."""
from __future__ import annotations
import logging
from datetime import date, datetime
from typing import Iterator

import requests
import structlog

from app.db.base import SessionLocal
from app.market_data.models import MutualFund, NavHistory

logger = structlog.get_logger()

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

def fetch_amfi_nav() -> str:
    """Fetch raw NAV text from AMFI."""
    resp = requests.get(AMFI_URL, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_amfi_nav(raw_text: str) -> Iterator[dict]:
    """
    Parse AMFI pipe-delimited NAV text.

    AMFI format has category headers interspersed — lines ending with ';'
    or lines that don't have 6 pipe-delimited fields are skipped.
    Malformed rows are logged and skipped, never raised.
    """
    for line in raw_text.strip().splitlines():
        line = line.strip()
        # Skip empty lines and category header lines (end with ';' or have no pipes)
        if not line or line.endswith(';') or '|' not in line:
            continue
        # Skip the header row itself
        if line.startswith('Scheme Code'):
            continue
        parts = line.split('|')
        if len(parts) != 6:
            logger.warning("amfi_parse_skip", reason="wrong_field_count", line=line[:80])
            continue
        scheme_code_str, _, _, scheme_name, nav_str, date_str = parts
        # Validate scheme code is integer
        try:
            scheme_code = str(int(scheme_code_str.strip()))
        except ValueError:
            logger.warning("amfi_parse_skip", reason="invalid_scheme_code", value=scheme_code_str)
            continue
        # Validate NAV
        try:
            nav = float(nav_str.strip())
            if nav <= 0:
                raise ValueError("non-positive NAV")
        except ValueError:
            logger.warning("amfi_parse_skip", reason="invalid_nav", value=nav_str)
            continue
        # Parse date: DD-Mon-YYYY
        try:
            nav_date = datetime.strptime(date_str.strip(), "%d-%b-%Y").date()
        except ValueError:
            logger.warning("amfi_parse_skip", reason="invalid_date", value=date_str)
            continue
        yield {
            "scheme_code": scheme_code,
            "scheme_name": scheme_name.strip(),
            "nav": nav,
            "nav_date": nav_date,
        }


def upsert_nav_history(records: list[dict], session) -> tuple[int, int]:
    """
    Insert NAV records. Skip duplicates (idempotent via PK).
    Returns (inserted, skipped).
    """
    inserted = 0
    skipped = 0

    # First, get all known scheme_codes from mutual_funds
    known_codes = {r[0] for r in session.query(MutualFund.scheme_code).all()}

    for record in records:
        scheme_code = record["scheme_code"]
        # Only insert nav_history for known funds (FK constraint)
        if scheme_code not in known_codes:
            skipped += 1
            continue

        # Check if already exists (PK: scheme_code + nav_date)
        existing = session.get(NavHistory, (scheme_code, record["nav_date"]))
        if existing is not None:
            skipped += 1
            continue

        nav_row = NavHistory(
            scheme_code=scheme_code,
            nav_date=record["nav_date"],
            nav=record["nav"],
        )
        session.add(nav_row)
        inserted += 1

        # Commit in batches
        if inserted % 500 == 0:
            session.commit()
            logger.info("amfi_upsert_progress", inserted=inserted)

    session.commit()
    return inserted, skipped


def run() -> int:
    """Main entry point for AMFI ingestion job. Returns count of inserted rows."""
    logger.info("amfi_job_start")
    try:
        raw = fetch_amfi_nav()
        records = list(parse_amfi_nav(raw))
        logger.info("amfi_parsed", record_count=len(records))

        session = SessionLocal()
        try:
            inserted, skipped = upsert_nav_history(records, session)
            logger.info("amfi_job_complete", inserted=inserted, skipped=skipped)
        finally:
            session.close()
        return inserted
    except Exception as e:
        logger.error("amfi_job_failed", error=str(e))
        raise


if __name__ == "__main__":
    run()
