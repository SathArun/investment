from __future__ import annotations
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def _run_amfi():
    from app.jobs.ingest_amfi import run
    run()


def _run_equity():
    from app.jobs.ingest_equity import run
    run()


def _run_nps():
    from app.jobs.ingest_nps import run
    run()


def _run_compute_metrics():
    from app.jobs.compute_metrics import run
    run()


def _run_compute_scores():
    from app.jobs.compute_scores import run
    run()


def _run_mfapi_backfill():
    from app.jobs.ingest_mfapi import run
    run()


scheduler.add_job(
    _run_amfi,
    trigger=CronTrigger(hour=23, minute=30),
    id="ingest_amfi",
    name="AMFI daily NAV ingestion",
    replace_existing=True,
)

scheduler.add_job(
    _run_equity,
    trigger=CronTrigger(day_of_week="mon-fri", hour=16, minute=30),
    id="ingest_equity",
    name="Equity index ingestion (weekdays)",
    replace_existing=True,
)

scheduler.add_job(
    _run_nps,
    trigger=CronTrigger(day_of_week="mon", hour=7, minute=0),
    id="ingest_nps",
    name="NPS returns ingestion (Mondays)",
    replace_existing=True,
)

scheduler.add_job(
    _run_compute_metrics,
    trigger=CronTrigger(hour=1, minute=0),
    id="compute_metrics",
    name="Compute metrics (nightly stub)",
    replace_existing=True,
)

scheduler.add_job(
    _run_mfapi_backfill,
    trigger=CronTrigger(day_of_week="sun", hour=2, minute=0),
    id="ingest_mfapi_backfill",
    name="mfapi historical backfill (weekly)",
    replace_existing=True,
)


scheduler.add_job(
    _run_compute_scores,
    trigger=CronTrigger(hour=0, minute=0),
    id="compute_scores",
    name="Compute advisor scores (nightly)",
    replace_existing=True,
)


def start() -> None:
    """Start the background scheduler."""
    logger.info("Starting APScheduler background scheduler")
    if not scheduler.running:
        scheduler.start()


def stop() -> None:
    """Stop the background scheduler."""
    logger.info("Stopping APScheduler background scheduler")
    scheduler.shutdown(wait=False)
