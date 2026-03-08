from __future__ import annotations
import threading
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_advisor
from app.db.base import get_db
from app.admin.models import JobRun
from app.admin.service import get_job_history, JOB_NAMES
from app.jobs.scheduler import (
    _run_amfi,
    _run_equity,
    _run_nps,
    _run_mfapi_backfill,
    _run_compute_metrics,
    _run_compute_scores,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

JOB_REGISTRY: dict[str, callable] = {
    "ingest_amfi": _run_amfi,
    "ingest_equity": _run_equity,
    "ingest_nps": _run_nps,
    "ingest_mfapi": _run_mfapi_backfill,
    "compute_metrics": _run_compute_metrics,
    "compute_scores": _run_compute_scores,
}


@router.get("/jobs")
def list_jobs(
    db: Session = Depends(get_db),
    _advisor_id: str = Depends(get_current_advisor),
):
    return {"jobs": get_job_history()}


@router.post("/jobs/{job_name}/run", status_code=202)
def trigger_job(
    job_name: str,
    db: Session = Depends(get_db),
    _advisor_id: str = Depends(get_current_advisor),
):
    if job_name not in JOB_REGISTRY:
        raise HTTPException(status_code=404, detail="Unknown job")

    existing = (
        db.query(JobRun)
        .filter(JobRun.job_name == job_name, JobRun.status == "running")
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Job already running")

    fn = JOB_REGISTRY[job_name]
    t = threading.Thread(target=fn, daemon=True)
    t.start()
    return {"status": "started", "job_name": job_name}
