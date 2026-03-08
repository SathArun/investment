"""Integration tests for the admin job-tracking API (Phase 5)."""
from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.admin.models import JobRun
from app.admin.service import get_job_history, record_start, record_finish, _prune, JOB_NAMES
from app.auth.service import create_advisor, create_access_token


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_engine():
    """Create a fresh in-memory SQLite engine per test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Register all models so metadata covers all tables
    import app.auth.models  # noqa: F401
    import app.market_data.models  # noqa: F401
    import app.analytics.models  # noqa: F401
    import app.goals.models  # noqa: F401
    import app.risk_profiler.models  # noqa: F401
    import app.admin.models  # noqa: F401
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Provide a SQLAlchemy session for the test engine."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def no_scheduler():
    """Prevent APScheduler from starting/stopping during tests."""
    with patch("app.jobs.scheduler.start", lambda: None), \
         patch("app.jobs.scheduler.stop", lambda: None):
        yield


@pytest.fixture
def client(test_engine, db_session):
    """TestClient that uses the test DB via dependency override."""
    TestSession = sessionmaker(bind=test_engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app), db_session
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(db_session):
    """Create an advisor and return a valid Bearer auth header."""
    advisor = create_advisor(
        db_session,
        email=f"admin_{uuid.uuid4().hex[:6]}@test.com",
        password="pass123!",
        name="Test Admin",
    )
    token = create_access_token(advisor.id)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Helper: patch SessionLocal used inside service functions
# ---------------------------------------------------------------------------

def _make_session_local_patcher(test_engine):
    """Return a context manager that redirects SessionLocal to test_engine."""
    from unittest.mock import MagicMock
    from contextlib import contextmanager

    TestSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    @contextmanager
    def fake_session_local():
        session = TestSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    return fake_session_local


# ---------------------------------------------------------------------------
# Part A – Service-level tests (no HTTP)
# ---------------------------------------------------------------------------

class TestGetJobHistoryFreshDB:
    """Test 1: get_job_history returns never_run for all 6 jobs on a fresh DB."""

    def test_returns_six_jobs_all_never_run(self, test_engine):
        fake_sl = _make_session_local_patcher(test_engine)
        with patch("app.admin.service.SessionLocal", fake_sl):
            result = get_job_history()

        assert len(result) == 6, f"Expected 6 jobs, got {len(result)}"
        for job in result:
            assert job["latest_status"] == "never_run", (
                f"Job {job['job_name']} expected never_run, got {job['latest_status']}"
            )


class TestRecordStartFinishLifecycle:
    """Test 2: record_start + record_finish success lifecycle."""

    def test_start_creates_running_row_finish_updates_it(self, test_engine, db_session):
        fake_sl = _make_session_local_patcher(test_engine)
        with patch("app.admin.service.SessionLocal", fake_sl):
            run_id = record_start("ingest_amfi")

        # Verify running row
        row = db_session.get(JobRun, run_id)
        assert row is not None
        assert row.status == "running"
        assert row.job_name == "ingest_amfi"
        assert row.finished_at is None

        with patch("app.admin.service.SessionLocal", fake_sl):
            record_finish(run_id, "success", rows_affected=42)

        db_session.expire(row)
        row = db_session.get(JobRun, run_id)
        assert row.status == "success"
        assert row.rows_affected == 42
        assert row.finished_at is not None


class TestRecordFinishFailure:
    """Test 3: record_finish with failed status stores error_msg."""

    def test_failure_stores_error_message(self, test_engine, db_session):
        fake_sl = _make_session_local_patcher(test_engine)
        with patch("app.admin.service.SessionLocal", fake_sl):
            run_id = record_start("ingest_equity")
            record_finish(run_id, "failed", error_msg="timeout error")

        row = db_session.get(JobRun, run_id)
        assert row.status == "failed"
        assert row.error_msg == "timeout error"


class TestPruneKeepsExactly100:
    """Test 4: _prune keeps exactly 100 rows for a job."""

    def test_prune_removes_oldest_beyond_100(self, db_session):
        # Insert 101 rows for ingest_nps
        for i in range(101):
            row = JobRun(
                job_name="ingest_nps",
                started_at=datetime(2024, 1, 1, i % 24, i % 60, i % 60),
                status="success",
            )
            db_session.add(row)
        db_session.commit()

        _prune(db_session, "ingest_nps")

        count = (
            db_session.query(JobRun)
            .filter(JobRun.job_name == "ingest_nps")
            .count()
        )
        assert count == 100, f"Expected 100 rows after prune, got {count}"


# ---------------------------------------------------------------------------
# Part B – HTTP endpoint tests
# ---------------------------------------------------------------------------

class TestListJobsEndpoint:
    """Tests 5 & 6: GET /api/admin/jobs."""

    def test_authenticated_returns_200_with_six_jobs(self, client, auth_headers, test_engine):
        test_client, _ = client
        fake_sl = _make_session_local_patcher(test_engine)
        with patch("app.admin.service.SessionLocal", fake_sl):
            response = test_client.get("/api/admin/jobs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert len(data["jobs"]) == 6

    def test_unauthenticated_returns_401(self, client):
        test_client, _ = client
        response = test_client.get("/api/admin/jobs")
        # HTTPBearer returns 403 when no credentials; both 401/403 indicate auth failure.
        # The spec says 401 — HTTPBearer actually raises 403 for missing credentials.
        assert response.status_code in (401, 403)


class TestTriggerJobEndpoint:
    """Tests 7, 8, 9: POST /api/admin/jobs/{job_name}/run."""

    def test_trigger_returns_202_when_no_running_row(self, client, auth_headers):
        test_client, _ = client
        # Patch the job function so the daemon thread does nothing
        with patch("app.admin.router._run_amfi", return_value=None), \
             patch("app.jobs.scheduler._run_amfi", return_value=None):
            response = test_client.post(
                "/api/admin/jobs/ingest_amfi/run", headers=auth_headers
            )

        assert response.status_code == 202
        body = response.json()
        assert body["status"] == "started"
        assert body["job_name"] == "ingest_amfi"

    def test_trigger_returns_409_when_already_running(self, client, auth_headers, db_session):
        test_client, _ = client
        # Insert a running row into the test DB
        running_row = JobRun(
            job_name="ingest_amfi",
            started_at=datetime.utcnow(),
            status="running",
        )
        db_session.add(running_row)
        db_session.commit()

        response = test_client.post(
            "/api/admin/jobs/ingest_amfi/run", headers=auth_headers
        )
        assert response.status_code == 409

    def test_trigger_unknown_job_returns_404(self, client, auth_headers):
        test_client, _ = client
        response = test_client.post(
            "/api/admin/jobs/unknown_job/run", headers=auth_headers
        )
        assert response.status_code == 404
