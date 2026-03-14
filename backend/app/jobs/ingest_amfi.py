"""AMFI daily NAV ingestion job."""
from __future__ import annotations
import re
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

# Maps AMFI category substrings (lowercased) → asset_class_id
_AMFI_CATEGORY_MAP: list[tuple[str, str]] = [
    ("large cap",           "eq_largecap"),
    ("mid cap",             "eq_midcap"),
    ("small cap",           "eq_smallcap"),
    ("flexi cap",           "eq_flexicap"),
    ("multi cap",           "eq_flexicap"),
    ("focused fund",        "eq_flexicap"),
    ("elss",                "eq_elss"),
    ("equity linked saving","eq_elss"),
    ("index fund",          "eq_index"),
    ("exchange traded",     "eq_index"),
    ("etf",                 "eq_index"),
    ("balanced advantage",  "eq_balanced"),
    ("aggressive hybrid",   "eq_balanced"),
    ("conservative hybrid", "eq_balanced"),
    ("multi asset",         "eq_balanced"),
    ("liquid fund",         "debt_liquid"),
    ("overnight fund",      "debt_liquid"),
    ("ultra short",         "debt_shortterm"),
    ("low duration",        "debt_shortterm"),
    ("short duration",      "debt_shortterm"),
    ("money market",        "debt_shortterm"),
    ("corporate bond",      "debt_corporate"),
    ("credit risk",         "debt_corporate"),
    ("banking and psu",     "debt_corporate"),
    ("gilt",                "debt_gilt"),
    ("gold",                "gold_etf"),
]


def _amfi_category_to_asset_class_id(amfi_category: str | None) -> str | None:
    """Return asset_class_id for a given AMFI category string, or None if unmapped."""
    if not amfi_category:
        return None
    lower = amfi_category.lower()
    for keyword, ac_id in _AMFI_CATEGORY_MAP:
        if keyword in lower:
            return ac_id
    return None


def _extract_sebi_category(header_line: str) -> str | None:
    """
    Extract the SEBI sub-category from an AMFI header line.
    Handles both:
      'Open Ended Schemes(Equity Scheme - Large Cap Fund)'  → 'Large Cap Fund'
      'Large Cap Fund'                                       → 'Large Cap Fund'
    """
    m = re.search(r'\(([^)]+)\)', header_line)
    if m:
        inner = m.group(1)
        # Remove prefix like 'Equity Scheme - '
        if ' - ' in inner:
            return inner.split(' - ', 1)[1].strip()
        return inner.strip()
    # Plain category line (no parens)
    return header_line.strip() or None


def fetch_amfi_nav() -> str:
    """Fetch raw NAV text from AMFI."""
    resp = requests.get(AMFI_URL, timeout=30, headers=AMFI_HEADERS)
    resp.raise_for_status()
    return resp.text


def parse_amfi_nav(raw_text: str) -> Iterator[dict]:
    """
    Parse AMFI semicolon-delimited NAV text.

    Category header lines (no ';') are tracked and attached to subsequent fund rows.
    Malformed rows are logged and skipped, never raised.
    """
    current_category: str | None = None
    for line in raw_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Lines without ';' are category headers or blank separators
        if ';' not in line:
            category = _extract_sebi_category(line)
            if category:
                current_category = category
            continue
        if line.startswith('Scheme Code'):
            continue
        parts = line.split(';')
        if len(parts) != 6:
            logger.warning("amfi_parse_skip", reason="wrong_field_count", line=line[:80])
            continue
        scheme_code_str, _, _, scheme_name, nav_str, date_str = parts
        try:
            scheme_code = str(int(scheme_code_str.strip()))
        except ValueError:
            logger.warning("amfi_parse_skip", reason="invalid_scheme_code", value=scheme_code_str)
            continue
        try:
            nav = float(nav_str.strip())
            if nav <= 0:
                raise ValueError("non-positive NAV")
        except ValueError:
            logger.warning("amfi_parse_skip", reason="invalid_nav", value=nav_str)
            continue
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
            "amfi_category": current_category,
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
    # Also update amfi_category / asset_class_id for existing rows that lack them.
    existing_funds: dict[str, MutualFund] = {
        mf.scheme_code: mf
        for mf in session.query(MutualFund).all()
    }
    new_funds = 0
    updated_funds = 0
    for record in records:
        scheme_code = record["scheme_code"]
        amfi_cat = record.get("amfi_category")
        ac_id = _amfi_category_to_asset_class_id(amfi_cat)
        if scheme_code not in existing_funds:
            mf = MutualFund(
                scheme_code=scheme_code,
                scheme_name=record["scheme_name"],
                amfi_category=amfi_cat,
                asset_class_id=ac_id,
                is_active=True,
            )
            session.add(mf)
            existing_funds[scheme_code] = mf
            new_funds += 1
        else:
            mf = existing_funds[scheme_code]
            # Back-fill missing category/asset_class on existing rows
            if amfi_cat and not mf.amfi_category:
                mf.amfi_category = amfi_cat
                updated_funds += 1
            if ac_id and not mf.asset_class_id:
                mf.asset_class_id = ac_id

    if new_funds or updated_funds:
        session.flush()
        logger.info("amfi_funds_synced", new_funds=new_funds, updated_funds=updated_funds)

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
    logger.info("amfi_upsert_done", new_funds=new_funds, updated_funds=updated_funds, inserted=inserted, skipped=skipped)
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
