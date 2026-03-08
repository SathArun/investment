---
title: "Phase 2: Backend Service & API"
status: completed
version: "1.0"
phase: 2
---

# Phase 2: Backend Service & API

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Implementation Examples]` — `record_start`, `record_finish`, `_prune`, trigger endpoint, concurrency guard walkthrough
- `[ref: SDD/Internal API Changes]` — `GET /api/admin/jobs` and `POST /api/admin/jobs/{job_name}/run` full request/response spec
- `[ref: SDD/Integration Points]` — scheduler.py → job_runs write pattern; router → thread spawn
- `[ref: SDD/Error Handling]` — 404 unknown job, 409 already running, re-raise on failure
- `backend/app/market_data/router.py` — canonical router pattern (prefix, tags, Depends)
- `backend/app/jobs/scheduler.py` — 6 `_run_*()` wrappers to be modified

**Key Decisions**:
- ADR-1: All tracking logic lives in `scheduler.py` wrappers, not in individual job files
- ADR-2: Concurrency guard queries DB for `status='running'` row before spawning thread
- ADR-4: `_prune()` runs inside `record_finish` — keeps last 100 rows per job

**Dependencies**:
- Phase 1 complete: `job_runs` table and `JobRun` model must exist

---

## Tasks

Provides the data access layer, the two admin API endpoints, and the scheduler instrumentation.

- [ ] **T2.1 Admin service — record_start, record_finish, _prune, get_job_history** `[activity: backend-api]`

  1. Prime: Read `SDD/Implementation Examples` section "scheduler.py tracking wrapper pattern" for the exact function signatures and session-per-call pattern. Read `backend/app/db/base.py` for `SessionLocal`. Read `SDD/Internal API Changes` for the `JobSummary` + `RunRow` response shape. `[ref: SDD/Implementation Examples]` `[ref: SDD/Internal API Changes]`
  2. Test: Write unit tests for: (a) `record_start("ingest_amfi")` inserts a row with `status="running"` and returns the new `id`; (b) `record_finish(run_id, "success", rows_affected=10)` updates the row to `status="success"` with `finished_at` set and `rows_affected=10`; (c) `record_finish(run_id, "failed", error_msg="timeout")` sets `status="failed"` with `error_msg`; (d) `get_job_history()` returns a list with one entry per known job name — including jobs with no runs (`latest_status="never_run"`); (e) `_prune()` deletes rows beyond 100 for a given job name.
  3. Implement: Create `backend/app/admin/service.py` with:
     - `JOB_NAMES = ["ingest_amfi", "ingest_equity", "ingest_nps", "ingest_mfapi", "compute_metrics", "compute_scores"]`
     - `record_start(job_name: str) -> int` — opens `SessionLocal`, inserts `JobRun`, commits, returns `run.id`
     - `record_finish(run_id: int, status: str, *, rows_affected=None, error_msg=None)` — updates row, calls `_prune(db, job_name)`
     - `_prune(db, job_name: str)` — deletes rows beyond top-100 by `started_at DESC` for that job
     - `get_job_history() -> list[dict]` — for each job in `JOB_NAMES`: query last 10 runs ordered by `started_at DESC`; compute `latest_status` (first row's status, or `"never_run"`); compute `latest_duration_seconds` from `finished_at - started_at`; return list of `JobSummary` dicts matching the API spec
  4. Validate: All unit tests pass. `pytest backend/tests/` clean. Typecheck passes.
  5. Success:
     - [ ] `record_start` + `record_finish` correctly persist a full job lifecycle to `job_runs` `[ref: SDD/Implementation Examples]`
     - [ ] `get_job_history()` returns `never_run` for a job with no history `[ref: PRD/Feature 1 AC — "Never run" status badge]`
     - [ ] `_prune()` keeps exactly 100 rows when called after the 101st insert `[ref: SDD/ADR-4]`

- [ ] **T2.2 Admin router — GET /jobs and POST /jobs/{name}/run** `[activity: backend-api]`

  1. Prime: Read `SDD/Internal API Changes` for endpoint specs (paths, status codes, response shapes). Read `SDD/Implementation Examples` "Concurrency guard" section for the traced walkthrough. Read `backend/app/clients/router.py` for the exact Depends pattern and `HTTPException` usage. `[ref: SDD/Internal API Changes]` `[ref: SDD/Implementation Examples]`
  2. Test: Write FastAPI `TestClient` tests for: (a) `GET /api/admin/jobs` returns 200 with `jobs` array of 6 entries; (b) `GET /api/admin/jobs` returns 401 without JWT; (c) `POST /api/admin/jobs/ingest_amfi/run` returns 202 when no running row exists; (d) `POST /api/admin/jobs/ingest_amfi/run` returns 409 when a `status="running"` row exists; (e) `POST /api/admin/jobs/unknown_job/run` returns 404; (f) `POST /api/admin/jobs/ingest_amfi/run` with valid JWT returns 202 and spawns a thread (assert thread is started, not that job completes).
  3. Implement: Create `backend/app/admin/router.py` with `APIRouter(prefix="/api/admin", tags=["admin"])`. Import `_run_*` wrappers from `scheduler.py` and define `JOB_REGISTRY` dict. `GET /jobs`: call `get_job_history()` and return `{"jobs": result}`. `POST /jobs/{job_name}/run`: validate against `JOB_REGISTRY` (404 if unknown); query DB for `status="running"` row (409 if found); spawn `threading.Thread(target=fn, daemon=True)`; return `{"status": "started", "job_name": job_name}` with 202.
  4. Validate: All router tests pass. No 500 errors on any tested path.
  5. Success:
     - [ ] `GET /api/admin/jobs` responds with correct shape including all 6 job names `[ref: SDD/Internal API Changes]`
     - [ ] `POST /run` returns 409 when a running row exists (concurrency guard works) `[ref: SDD/ADR-2]` `[ref: PRD/Feature 2 AC — "Job already running" message]`
     - [ ] All admin endpoints return 401 for unauthenticated requests `[ref: PRD/Feature 4 AC — auth required]`

- [ ] **T2.3 Scheduler wrappers — add tracking + job return values** `[activity: backend-api]`

  1. Prime: Read `SDD/Implementation Examples` "scheduler.py tracking wrapper pattern" for the exact try/finally/re-raise structure. Read `backend/app/jobs/scheduler.py` for all 6 `_run_*()` functions. Read each of the 6 job files to understand what `run()` currently returns (likely `None`) and where to add `return total_rows_int`. `[ref: SDD/Implementation Examples]` `[ref: SDD/Implementation Gotchas — "run() return value change"]`
  2. Test: Write tests that mock `record_start` and `record_finish` and verify: (a) `_run_amfi()` calls `record_start("ingest_amfi")` then calls `run()` then calls `record_finish(run_id, "success", rows_affected=N)`; (b) when `run()` raises, `_run_amfi()` calls `record_finish(run_id, "failed", error_msg=...)` and re-raises; (c) `record_finish` is always called even on exception (`finally` semantics).
  3. Implement: (a) In each of the 6 job files (`ingest_amfi.py`, `ingest_equity.py`, `ingest_nps.py`, `ingest_mfapi.py`, `compute_metrics.py`, `compute_scores.py`): add `return total_inserted` (or equivalent count integer) at the end of `run()`. (b) In `backend/app/jobs/scheduler.py`: add imports from `app.admin.service`; wrap each `_run_*()` with `run_id = record_start(...)` / `try: rows = run(); record_finish(run_id, "success", rows_affected=rows)` / `except Exception as e: record_finish(run_id, "failed", error_msg=str(e)); raise`.
  4. Validate: Existing job tests still pass. New wrapper tests pass. Manually run one job wrapper and verify a row appears in `job_runs`. `pytest` clean.
  5. Success:
     - [ ] Every `_run_*()` wrapper writes a complete `job_runs` record (start + finish) for both success and failure paths `[ref: SDD/ADR-1]` `[ref: PRD/Feature 1 AC — run history visible]`
     - [ ] On job failure, the exception is re-raised so APScheduler continues to log it `[ref: SDD/Error Handling]`
     - [ ] Each job's `run()` returns an integer rows-affected count `[ref: SDD/Implementation Gotchas]`

- [ ] **T2.4 Register admin router in main.py** `[activity: backend-api]`

  1. Prime: Read `backend/app/main.py` — specifically the `include_router` calls and lifespan function. `[ref: SDD/Building Block View/Directory Map]`
  2. Test: Write a test that calls `GET /api/admin/jobs` via `TestClient(app)` — assert 401 (endpoint exists but unauthenticated). This verifies the router is mounted.
  3. Implement: In `backend/app/main.py`, add `from app.admin.router import router as admin_router` and `app.include_router(admin_router)` alongside the other routers.
  4. Validate: App starts without import errors. `GET /api/admin/jobs` via curl or test client returns 401 (not 404).
  5. Success:
     - [ ] `GET /api/admin/jobs` and `POST /api/admin/jobs/{name}/run` are reachable at the declared paths `[ref: SDD/Internal API Changes]`

- [ ] **T2.5 Phase 2 Validation** `[activity: validate]`

  - Run full `pytest` suite. Verify 0 regressions in existing tests. Run `GET /api/admin/jobs` with a valid JWT and confirm the response shape matches the SDD specification. Trigger `POST /api/admin/jobs/ingest_amfi/run` and confirm a `running` row appears in `job_runs`, then a `success` row after completion.
