"""Admin service: job run tracking helpers."""
from __future__ import annotations
from datetime import datetime

from app.db.base import SessionLocal
from app.admin.models import JobRun

JOB_NAMES = [
    "ingest_amfi",
    "ingest_equity",
    "ingest_nps",
    "ingest_mfapi",
    "compute_metrics",
    "compute_scores",
]


def record_start(job_name: str) -> int:
    """Create a new JobRun row with status='running'. Returns run.id."""
    with SessionLocal() as db:
        run = JobRun(
            job_name=job_name,
            started_at=datetime.utcnow(),
            status="running",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.id


def record_finish(
    run_id: int,
    status: str,
    *,
    rows_affected: int | None = None,
    error_msg: str | None = None,
) -> None:
    """Update an existing JobRun row with finish info, then prune old rows."""
    with SessionLocal() as db:
        run = db.get(JobRun, run_id)
        if run is not None:
            run.finished_at = datetime.utcnow()
            run.status = status
            run.rows_affected = rows_affected
            run.error_msg = error_msg
            db.commit()
            _prune(db, run.job_name)


def _prune(db, job_name: str) -> None:
    """Delete rows for job_name beyond the 100 most recent (by started_at DESC)."""
    keep_ids = (
        db.query(JobRun.id)
        .filter(JobRun.job_name == job_name)
        .order_by(JobRun.started_at.desc())
        .limit(100)
        .scalar_subquery()
    )
    db.query(JobRun).filter(
        JobRun.job_name == job_name,
        ~JobRun.id.in_(keep_ids),
    ).delete(synchronize_session=False)
    db.commit()


def mark_stale_running_jobs() -> int:
    """
    On server startup, any job_runs still in 'running' status were interrupted
    by a process restart. Mark them as 'interrupted' so the UI doesn't show
    a forever-running job.
    Returns the number of rows updated.
    """
    with SessionLocal() as db:
        stale = db.query(JobRun).filter(JobRun.status == "running").all()
        now = datetime.utcnow()
        for run in stale:
            run.status = "interrupted"
            run.finished_at = now
            run.error_msg = "Server restarted before job finished"
        db.commit()
        return len(stale)


def get_job_history() -> list[dict]:
    """Return last 10 runs for each known job, plus summary fields."""
    result = []
    with SessionLocal() as db:
        for name in JOB_NAMES:
            runs = (
                db.query(JobRun)
                .filter(JobRun.job_name == name)
                .order_by(JobRun.started_at.desc())
                .limit(10)
                .all()
            )

            if runs:
                first = runs[0]
                latest_status = first.status
                latest_started_at = first.started_at.isoformat()
                if first.started_at and first.finished_at:
                    latest_duration_seconds = (
                        first.finished_at - first.started_at
                    ).total_seconds()
                else:
                    latest_duration_seconds = None
            else:
                latest_status = "never_run"
                latest_started_at = None
                latest_duration_seconds = None

            run_rows = [
                {
                    "id": run.id,
                    "started_at": run.started_at.isoformat(),
                    "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                    "status": run.status,
                    "duration_seconds": (
                        (run.finished_at - run.started_at).total_seconds()
                        if run.finished_at
                        else None
                    ),
                    "rows_affected": run.rows_affected,
                    "error_msg": run.error_msg,
                }
                for run in runs
            ]

            result.append(
                {
                    "job_name": name,
                    "latest_status": latest_status,
                    "latest_started_at": latest_started_at,
                    "latest_duration_seconds": latest_duration_seconds,
                    "runs": run_rows,
                }
            )
    return result
