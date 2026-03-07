from __future__ import annotations
import structlog
import requests

from app.db.base import SessionLocal
from app.market_data.models import MutualFund

logger = structlog.get_logger()

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"


def fetch_nav_text() -> str:
    """Fetch raw NAV text from AMFI."""
    resp = requests.get(AMFI_URL, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_fund_catalog(raw_text: str) -> list[dict]:
    """
    Parse AMFI NAV text to extract fund catalog entries.

    Category header rows end with ';' — these set the current category context.
    Data rows with 6 pipe-delimited fields are extracted: scheme_code, scheme_name,
    and the last seen amfi_category.
    """
    current_category: str | None = None
    funds: list[dict] = []

    for line in raw_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        # Category header rows end with ';'
        if line.endswith(";") and "|" not in line:
            current_category = line.rstrip(";").strip()
            continue

        # Skip column header row
        if line.startswith("Scheme Code"):
            continue

        # Data rows must be pipe-delimited with 6 fields
        if "|" not in line:
            continue

        parts = line.split("|")
        if len(parts) != 6:
            logger.warning("seed_fund_catalog_skip", reason="wrong_field_count", line=line[:80])
            continue

        scheme_code_str = parts[0].strip()
        scheme_name = parts[3].strip()

        try:
            scheme_code = str(int(scheme_code_str))
        except ValueError:
            logger.warning("seed_fund_catalog_skip", reason="invalid_scheme_code", value=scheme_code_str)
            continue

        funds.append({
            "scheme_code": scheme_code,
            "scheme_name": scheme_name,
            "amfi_category": current_category,
        })

    return funds


def upsert_fund_catalog(funds: list[dict], session) -> tuple[int, int]:
    """
    Insert mutual fund catalog entries. Skip existing schemes (by scheme_code).
    Returns (inserted, skipped).
    """
    inserted = 0
    skipped = 0

    existing_codes = {r[0] for r in session.query(MutualFund.scheme_code).all()}

    for fund in funds:
        scheme_code = fund["scheme_code"]
        if scheme_code in existing_codes:
            skipped += 1
            continue

        row = MutualFund(
            scheme_code=scheme_code,
            scheme_name=fund["scheme_name"],
            amfi_category=fund["amfi_category"],
            is_active=True,
        )
        session.add(row)
        existing_codes.add(scheme_code)
        inserted += 1

        if inserted % 500 == 0:
            session.commit()
            logger.info("seed_fund_catalog_progress", inserted=inserted)

    session.commit()
    return inserted, skipped


def run() -> tuple[int, int]:
    """Main entry point for seeding the mutual fund catalog."""
    logger.info("seed_fund_catalog_start")
    try:
        raw = fetch_nav_text()
        funds = parse_fund_catalog(raw)
        logger.info("seed_fund_catalog_parsed", fund_count=len(funds))

        session = SessionLocal()
        try:
            inserted, skipped = upsert_fund_catalog(funds, session)
            logger.info("seed_fund_catalog_complete", inserted=inserted, skipped=skipped)
            return inserted, skipped
        finally:
            session.close()
    except Exception as e:
        logger.error("seed_fund_catalog_failed", error=str(e))
        raise


if __name__ == "__main__":
    run()
