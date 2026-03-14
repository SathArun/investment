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
AMFI_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
}

def fetch_amfi_nav() -> str:
    """Fetch raw NAV text from AMFI."""
    resp = requests.get(AMFI_URL, timeout=30, headers=AMFI_HEADERS)
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
    Insert NAV records. Auto-creates MutualFund catalog entries for unknown scheme codes,
    then inserts nav_history. Skip duplicates (idempotent via PK).
    Returns (inserted, skipped).

    Two-pass approach required because session uses autoflush=False:
      Pass 1 — create missing MutualFund rows and flush so the FK exists in the DB.
      Pass 2 — insert NavHistory rows (FK now satisfied).
    """
    # Pass 1: ensure every scheme_code has a MutualFund catalog row
    known_codes = {r[0] for r in session.query(MutualFund.scheme_code).all()}
    new_funds = 0
    for record in records:
        scheme_code = record["scheme_code"]
        if scheme_code not in known_codes:
            session.add(MutualFund(
                scheme_code=scheme_code,
                scheme_name=record["scheme_name"],
                is_active=True,
            ))
            known_codes.add(scheme_code)
            new_funds += 1

    if new_funds:
        session.flush()  # Push MutualFund rows to DB before NavHistory FK check
        logger.info("amfi_new_funds_flushed", new_funds=new_funds)

    # Pass 2: insert NAV history rows
    inserted = 0
    skipped = 0
    for record in records:
        existing = session.get(NavHistory, (record["scheme_code"], record["nav_date"]))
        if existing is not None:
            skipped += 1
            continue
        session.add(NavHistory(
            scheme_code=record["scheme_code"],
            nav_date=record["nav_date"],
            nav=record["nav"],
        ))
        inserted += 1
        if inserted % 500 == 0:
            session.commit()
            logger.info("amfi_upsert_progress", inserted=inserted)

    session.commit()
    logger.info("amfi_upsert_done", new_funds=new_funds, inserted=inserted, skipped=skipped)
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
