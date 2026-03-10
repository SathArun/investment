"""mfapi.in historical NAV backfill job."""
from __future__ import annotations
import time
from datetime import datetime
from typing import Optional

import requests
import structlog

from app.db.base import SessionLocal
from app.market_data.models import MutualFund, NavHistory

logger = structlog.get_logger()

MFAPI_BASE = "https://www.mfapi.in/mf"
RATE_LIMIT_BACKOFF_SECONDS = 60
REQUEST_DELAY_SECONDS = 0.5


def fetch_scheme_history(scheme_code: str, session=None) -> list[dict]:
    """
    Fetch historical NAV data for a single scheme from mfapi.in.
    Returns list of {"scheme_code", "nav_date", "nav"} dicts.
    Handles HTTP 429 with 60s backoff + retry.
    """
    url = f"{MFAPI_BASE}/{scheme_code}"
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 429:
                logger.warning("mfapi_rate_limited", scheme_code=scheme_code, backoff=RATE_LIMIT_BACKOFF_SECONDS)
                time.sleep(RATE_LIMIT_BACKOFF_SECONDS)
                continue
            resp.raise_for_status()
            payload = resp.json()
            records = []
            for row in payload.get("data", []):
                try:
                    nav_date = datetime.strptime(row["date"], "%d-%m-%Y").date()
                    nav = float(row["nav"])
                    if nav > 0:
                        records.append({
                            "scheme_code": str(scheme_code),
                            "nav_date": nav_date,
                            "nav": nav,
                        })
                except (ValueError, KeyError) as e:
                    logger.warning("mfapi_row_parse_error", scheme_code=scheme_code, row=row, error=str(e))
                    continue
            return records
        except requests.exceptions.RequestException as e:
            logger.error("mfapi_fetch_error", scheme_code=scheme_code, attempt=attempt, error=str(e))
            if attempt < 2:
                time.sleep(5)
    return []


def backfill_historical_nav(scheme_code: str, session) -> tuple[int, int]:
    """
    Backfill historical NAV for one scheme. Idempotent (skips existing rows).
    Returns (inserted, skipped).
    """
    records = fetch_scheme_history(scheme_code)
    inserted = 0
    skipped = 0
    for record in records:
        existing = session.get(NavHistory, (record["scheme_code"], record["nav_date"]))
        if existing is not None:
            skipped += 1
            continue
        row = NavHistory(
            scheme_code=record["scheme_code"],
            nav_date=record["nav_date"],
            nav=record["nav"],
        )
        session.add(row)
        inserted += 1
    if inserted > 0:
        session.commit()
    return inserted, skipped


def backfill_all_schemes(session, limit: Optional[int] = None) -> dict:
    """
    Backfill historical NAV for all active mutual funds.
    Skips schemes that already have ≥ 252 NAV rows (1 year of data — enough for metrics).
    Processes one scheme at a time with delay. Logs progress every 100 schemes.
    """
    from sqlalchemy import func
    from app.market_data.models import NavHistory

    query = session.query(MutualFund).filter(MutualFund.is_active == True)
    if limit:
        query = query.limit(limit)
    schemes = query.all()

    # Pre-fetch NAV row counts to avoid per-scheme queries
    counts = dict(
        session.query(NavHistory.scheme_code, func.count(NavHistory.nav_date))
        .group_by(NavHistory.scheme_code)
        .all()
    )

    total_inserted = 0
    total_skipped = 0
    already_sufficient = 0

    for i, fund in enumerate(schemes):
        if counts.get(fund.scheme_code, 0) >= 252:
            already_sufficient += 1
            continue
        try:
            inserted, skipped = backfill_historical_nav(fund.scheme_code, session)
            total_inserted += inserted
            total_skipped += skipped

            if (i + 1) % 100 == 0:
                logger.info("mfapi_backfill_progress", processed=i+1, total=len(schemes), inserted=total_inserted)

            time.sleep(REQUEST_DELAY_SECONDS)
        except Exception as e:
            logger.error("mfapi_scheme_error", scheme_code=fund.scheme_code, error=str(e))
            continue

    logger.info(
        "mfapi_backfill_complete",
        schemes_total=len(schemes),
        already_sufficient=already_sufficient,
        total_inserted=total_inserted,
    )
    return {"schemes_processed": len(schemes), "inserted": total_inserted, "skipped": total_skipped}


def run() -> int:
    """Main entry point. Returns total rows inserted."""
    logger.info("mfapi_job_start")
    with SessionLocal() as session:
        result = backfill_all_schemes(session)
    logger.info("mfapi_job_done", **result)
    return result.get("inserted", 0)


if __name__ == "__main__":
    run()
