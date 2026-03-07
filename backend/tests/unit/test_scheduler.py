"""Tests for APScheduler setup."""
from __future__ import annotations


def test_scheduler_has_six_jobs():
    """Scheduler should have exactly 6 registered jobs."""
    from app.jobs.scheduler import scheduler
    # Scheduler not started — just check registered jobs
    jobs = scheduler.get_jobs()
    assert len(jobs) == 6


def test_scheduler_job_ids():
    """All expected job IDs are registered."""
    from app.jobs.scheduler import scheduler
    job_ids = {j.id for j in scheduler.get_jobs()}
    assert "ingest_amfi" in job_ids
    assert "ingest_equity" in job_ids
    assert "ingest_nps" in job_ids
    assert "compute_metrics" in job_ids
    assert "ingest_mfapi_backfill" in job_ids
    assert "compute_scores" in job_ids


def test_scheduler_module_importable():
    """Scheduler module imports without errors."""
    import app.jobs.scheduler  # noqa: F401
    assert True


def test_seed_fund_catalog_importable():
    """seed_fund_catalog module imports without errors."""
    import app.jobs.seed_fund_catalog  # noqa: F401
    assert True
