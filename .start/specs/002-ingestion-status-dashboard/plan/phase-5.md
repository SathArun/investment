---
title: "Phase 5: Integration & E2E Validation"
status: completed
version: "1.0"
phase: 5
---

# Phase 5: Integration & E2E Validation

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: PRD/Feature Requirements]` — all 19 acceptance criteria (Features 1–4 + Should Haves)
- `[ref: SDD/Acceptance Criteria]` — EARS-format system-level criteria (20 items)
- `[ref: SDD/Runtime View]` — primary flow sequence and error handling table
- `[ref: SDD/Quality Requirements]` — performance, reliability, security criteria

**Key Decisions**:
- Integration tests run against a real SQLite test DB (not mocked) to verify the full scheduler → DB → API → response chain
- E2E walkthrough validates the primary user journey: stale job → Run Now → Running badge → Success → freshness bar updates

**Dependencies**:
- All previous phases complete (Phases 1–4)

---

## Tasks

Verifies all PRD acceptance criteria are met end-to-end. Catches integration gaps between scheduler tracking, API, and frontend behaviour.

- [ ] **T5.1 Backend integration tests — full admin API lifecycle** `[activity: backend-api]`

  1. Prime: Read `SDD/Acceptance Criteria` for all system-level criteria. Read `SDD/Runtime View/Error Handling` table. Review existing `backend/tests/` test files for `TestClient` and test DB fixture patterns. `[ref: SDD/Acceptance Criteria]` `[ref: SDD/Runtime View]`
  2. Test (these are the deliverable — write them now):
     - **Job history lifecycle:** Call `_run_amfi()` wrapper directly → assert `job_runs` row with `status="success"` and `rows_affected` is an integer.
     - **Failure recording:** Patch `ingest_amfi.run` to raise → call `_run_amfi()` → assert row has `status="failed"` and `error_msg` is set.
     - **GET /api/admin/jobs response shape:** Assert response has `jobs` array of 6 items; each has `job_name`, `latest_status`, `runs` list; the job just run has a non-null `latest_started_at`.
     - **GET /api/admin/jobs — never_run jobs:** Fresh test DB → assert all 6 jobs return `latest_status="never_run"`.
     - **POST /run → 202:** No running row in DB → `POST /api/admin/jobs/ingest_amfi/run` → 202 response.
     - **POST /run → 409:** Insert a `status="running"` row → `POST /api/admin/jobs/ingest_amfi/run` → 409 response.
     - **POST /run → 404:** `POST /api/admin/jobs/unknown_job/run` → 404.
     - **Prune keeps 100:** Insert 101 `job_runs` rows for `ingest_amfi` → call `_prune(db, "ingest_amfi")` → assert count is exactly 100.
     - **Auth guard:** All admin endpoints return 401 without JWT.
  3. Implement: Add `backend/tests/test_admin_api.py` with the tests above. Use a test-scoped SQLite DB fixture (in-memory or temp file). Ensure tests do not pollute the dev DB.
  4. Validate: `pytest backend/tests/test_admin_api.py -v` — all pass. No regressions in existing test suite.
  5. Success:
     - [ ] All 9 integration test scenarios pass `[ref: PRD/Feature 1 AC]` `[ref: PRD/Feature 2 AC]`
     - [ ] 0 regressions in existing backend tests

- [ ] **T5.2 Frontend component integration tests** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `SDD/Acceptance Criteria` frontend-facing items. Review `frontend/src/tests/` for existing component test patterns (React Testing Library + Vitest). `[ref: SDD/Acceptance Criteria]`
  2. Test (these are the deliverable — write them now):
     - **AdminPage — 6 cards rendered:** Mock `fetchJobs` to return 6 jobs → assert 6 `JobCard` elements render.
     - **AdminPage — Run Now triggers correctly:** Click "Run Now" on job with `status="success"` → assert `triggerJob` called with correct job name.
     - **AdminPage — disabled while running:** Mock one job with `latest_status="running"` → assert its "Run Now" button is disabled; other jobs' buttons are enabled.
     - **JobCard — never_run state:** Render with `latest_status="never_run"` → assert "Never run" text visible.
     - **JobCard — failed with error:** Render with run having `status="failed"`, `error_msg="timeout"` → assert "timeout" visible in history table.
     - **DataFreshnessBar — stale warning:** Pass `freshness` with `amfi` timestamp 72h ago → assert ⚠ stale text appears for AMFI.
     - **DataFreshnessBar — all fresh:** Pass all timestamps within 24h → assert no ⚠ icons.
     - **Dashboard — freshness bar rendered:** Mock `dashboardStore.dataFreshness` → assert `DataFreshnessBar` renders on dashboard.
     - **Auth redirect:** Render `/admin` without auth token → assert redirect to `/login`.
  3. Implement: Add `frontend/src/tests/AdminPage.test.tsx`, `frontend/src/tests/JobCard.test.tsx`, `frontend/src/tests/DataFreshnessBar.test.tsx`. Use existing test utilities from `frontend/src/tests/`.
  4. Validate: `npm test` — all new and existing tests pass. `npm run typecheck` clean.
  5. Success:
     - [ ] All 9 frontend component test scenarios pass `[ref: PRD/Feature 1–4 AC]`
     - [ ] 0 regressions in existing frontend tests

- [ ] **T5.3 PRD acceptance criteria coverage check** `[activity: validate]`

  1. Prime: Read `requirements.md` Feature 1–4 acceptance criteria (19 checkboxes). Read `solution.md` Acceptance Criteria section (20 EARS statements). `[ref: PRD/Feature Requirements]` `[ref: SDD/Acceptance Criteria]`
  2. Test: Manually trace each PRD checkbox to the task(s) that implement it. Flag any criterion not covered by a test.
  3. Implement: For any uncovered criterion, add a targeted test in the appropriate test file.
  4. Validate: Every PRD checkbox maps to at least one passing test. Every SDD EARS criterion is verifiable.
  5. Success:
     - [ ] All 19 PRD acceptance criteria have at least one corresponding test `[ref: PRD/Feature Requirements]`
     - [ ] All 20 SDD EARS criteria are verifiable through tests or manual steps `[ref: SDD/Acceptance Criteria]`

- [ ] **T5.4 E2E manual walkthrough — primary user journey** `[activity: validate]`

  1. Prime: Read `PRD/User Journey Maps — Morning Pre-Client Health Check` (5-step journey). `[ref: PRD/User Journey Maps]`
  2. Test: With both backend and frontend running:
     - Start: open `/dashboard` — freshness bar is visible
     - Navigate to `/admin` — 6 cards visible, including one failed job
     - Click "Run Now" on the failed job — badge changes to "Running" within 2 seconds
     - Wait for job to complete — new "Success" row appears in history table
     - Return to `/dashboard` — freshness bar reflects updated timestamp for that data source
     - Confirm no "Admin" link in nav bar on any page
     - Open a new browser tab and navigate to `/admin` without logging in — redirected to `/login`
  3. Implement: No code changes unless a step fails (create a fix task if needed).
  4. Validate: All 7 manual steps pass.
  5. Success:
     - [ ] Complete primary user journey executes without any terminal access `[ref: PRD/Value Proposition]`
     - [ ] Run Now → Running → Success lifecycle visible end-to-end `[ref: PRD/Feature 2 AC]`
     - [ ] Freshness bar updates after successful job run `[ref: PRD/Feature 3 AC]`
     - [ ] No Admin link in nav, `/admin` requires auth `[ref: PRD/Feature 4 AC]`

- [ ] **T5.5 Phase 5 Validation** `[activity: validate]`

  - Final checklist:
    - [ ] `pytest` — 0 failures, 0 regressions
    - [ ] `npm test` — 0 failures, 0 regressions
    - [ ] `npm run typecheck` — 0 errors
    - [ ] `npm run lint` — 0 errors
    - [ ] `alembic upgrade head` on a fresh DB — succeeds
    - [ ] All 19 PRD acceptance criteria verified
    - [ ] E2E manual walkthrough complete (T5.4)
