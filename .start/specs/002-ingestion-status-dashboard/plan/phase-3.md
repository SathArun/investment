---
title: "Phase 3: Frontend Admin Page"
status: completed
version: "1.0"
phase: 3
---

# Phase 3: Frontend Admin Page

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Application Data Models]` — `AdminJobSummary` and `RunRow` TypeScript types
- `[ref: SDD/Implementation Examples]` — `adminStore.ts` adaptive polling pattern
- `[ref: SDD/User Interface & UX]` — ASCII wireframe for `/admin` page; component state diagram for Run Now button
- `[ref: SDD/Internal API Changes]` — `GET /api/admin/jobs` response shape to match
- `frontend/src/store/goalStore.ts` — canonical Zustand store pattern
- `frontend/src/App.tsx` — `AppNav` component and `ProtectedRoute` pattern

**Key Decisions**:
- ADR-3: Adaptive polling — 5s when any job is running, 30s otherwise. `useEffect` depends on `[jobs]` so interval is re-created on each jobs state change.
- The `Run Now` button must be disabled while `latest_status === 'running'` for that specific job; other jobs' buttons remain enabled.
- `/admin` uses `AppNav` with title `"System Health"` — not added to `NAV_LINKS` array.

**Dependencies**:
- Phase 2 complete: `GET /api/admin/jobs` and `POST /api/admin/jobs/{name}/run` must be available and returning correct shapes.

---

## Tasks

Delivers the complete `/admin` page with job cards, run history table, Run Now trigger, and adaptive polling.

- [ ] **T3.1 adminStore — Zustand store with fetchJobs and triggerJob** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/store/goalStore.ts` for the Zustand `create<State>()` pattern with `apiClient` calls. Read `SDD/Implementation Examples` for the exact `adminStore.ts` skeleton. Read `SDD/Application Data Models` for `AdminJobSummary` and `RunRow` type shapes. `[ref: SDD/Implementation Examples]` `[ref: SDD/Application Data Models]`
  2. Test: Write unit tests (with `apiClient` mocked) for: (a) `fetchJobs()` sets `jobs` from API response; (b) `fetchJobs()` sets `isLoading: true` during fetch then `false` after; (c) `triggerJob("ingest_amfi")` calls `POST /admin/jobs/ingest_amfi/run` then immediately calls `GET /admin/jobs`; (d) `triggerJob` when API returns 409 surfaces the error without crashing.
  3. Implement: Create `frontend/src/store/adminStore.ts`. Define `AdminJobSummary`, `RunRow` TypeScript interfaces. Define `AdminState` interface with `jobs: AdminJobSummary[]`, `isLoading: boolean`, `fetchJobs: () => Promise<void>`, `triggerJob: (jobName: string) => Promise<void>`. Implement using `create<AdminState>()`. `fetchJobs` calls `GET /api/admin/jobs`, sets `jobs: data.jobs`. `triggerJob` calls `POST /api/admin/jobs/${jobName}/run`, then calls `GET /api/admin/jobs` to refresh state.
  4. Validate: Unit tests pass. TypeScript types check (`npm run typecheck`). Store handles 409 without throwing.
  5. Success:
     - [ ] `fetchJobs()` correctly populates store with all 6 job summaries `[ref: SDD/Internal API Changes]`
     - [ ] `triggerJob()` refreshes jobs state immediately after POST, causing badge to show "Running" `[ref: PRD/Feature 2 AC — status changes to Running within 2 seconds]`

- [ ] **T3.2 JobCard and RunHistoryTable components** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `SDD/User Interface & UX` ASCII wireframe for card structure. Read `SDD/Application Data Models` for `AdminJobSummary` and `RunRow` field names. Study `frontend/src/components/Dashboard/AssetTable.tsx` for TailwindCSS table/card pattern. `[ref: SDD/User Interface & UX]` `[ref: SDD/Application Data Models]`
  2. Test: Write component tests (React Testing Library) for `JobCard`: (a) renders job name; (b) renders correct status badge colour for `"success"`, `"failed"`, `"running"`, `"never_run"`; (c) "Run Now" button is disabled when `latest_status === "running"`; (d) "Run Now" button fires `onRunNow` callback when clicked and job is not running. Write tests for `RunHistoryTable`: (a) renders up to 10 rows; (b) error column shows error message on failed rows; (c) shows `rows_affected` count on success rows.
  3. Implement: Create `frontend/src/components/Admin/JobCard.tsx`. Props: `job: AdminJobSummary`, `onRunNow: (jobName: string) => void`. Render: job name heading; status badge (green/red/blue/gray); last run timestamp and duration; "Run Now" button (disabled + spinner when `latest_status === "running"`); collapsible `RunHistoryTable`. Create `frontend/src/components/Admin/RunHistoryTable.tsx`. Props: `runs: RunRow[]`. Render: table with columns Timestamp, Status, Duration, Rows, Error. Show `—` for null values.
  4. Validate: Component tests pass. No TypeScript errors. Visual: badge colours match status — green for success, red for failed, blue for running, gray for never_run.
  5. Success:
     - [ ] "Run Now" button disabled only for the specific running job; other cards remain enabled `[ref: PRD/Feature 2 AC — only running job is locked]`
     - [ ] Error message visible in history table row for failed runs `[ref: PRD/Feature 1 AC — error message visible]`
     - [ ] "Never run" badge shown for jobs with no history `[ref: PRD/Feature 1 AC — Never run status]`

- [ ] **T3.3 AdminPage with adaptive polling and /admin route** `[activity: frontend-ui]`

  1. Prime: Read `SDD/Implementation Examples` for the exact `useEffect` adaptive polling pattern. Read `frontend/src/App.tsx` for `AppNav`, `ProtectedRoute`, and route definition patterns. Review `SDD/Runtime View` primary flow sequence. `[ref: SDD/Implementation Examples]` `[ref: SDD/Runtime View]`
  2. Test: Write tests for `AdminPage`: (a) fetches jobs on mount; (b) renders 6 `JobCard` components when store has 6 jobs; (c) passes `triggerJob` as `onRunNow` to each card; (d) polling interval is 5000ms when `latest_status === "running"` exists in jobs; (e) polling interval is 30000ms when no jobs are running. Write route test: (a) `/admin` renders `AdminPage` when authenticated; (b) `/admin` redirects to `/login` when unauthenticated.
  3. Implement: Create page component (inline in `App.tsx` or as a separate file following the `GoalsPage` / `RiskProfilerPage` pattern): `AdminPage` uses `useAdminStore`, calls `fetchJobs()` on mount, renders `AppNav` with `title="System Health"`, renders 6 `JobCard` components in a responsive grid. Add `useEffect` for adaptive polling: `hasRunning ? 5_000 : 30_000` interval. Add `/admin` route to `App.tsx` `<Routes>` as `<ProtectedRoute><AdminPage /></ProtectedRoute>`. Do NOT add "Admin" or "System Health" to `NAV_LINKS`.
  4. Validate: `npm run typecheck` clean. Navigate to `/admin` when logged in — page loads. Navigate to `/admin` when logged out — redirects to `/login`. No "Admin" link appears in nav bar on any page.
  5. Success:
     - [ ] `/admin` loads and displays 6 job cards when authenticated `[ref: PRD/Feature 4 AC — page loads with all job cards]`
     - [ ] `/admin` redirects to `/login` when unauthenticated `[ref: PRD/Feature 4 AC — unauthenticated redirect]`
     - [ ] No "Admin" or "System Health" link in `AppNav` navigation `[ref: PRD/Feature 4 AC — not in main nav]`
     - [ ] Page auto-refreshes every 30s at rest; switches to 5s when a job is running `[ref: PRD/Should Have — auto-refresh]`

- [ ] **T3.4 Phase 3 Validation** `[activity: validate]`

  - Run `npm test` — all new and existing tests pass. Run `npm run typecheck` and `npm run lint` — clean. End-to-end manual walkthrough: open `/admin`, click "Run Now" on one job, confirm badge changes to "Running", wait for completion, confirm new "Success" row appears in history table.
