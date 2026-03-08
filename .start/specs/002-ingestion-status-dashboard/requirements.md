---
title: "Ingestion Status Dashboard"
status: draft
version: "1.0"
---

# Product Requirements Document

## Validation Checklist

### CRITICAL GATES (Must Pass)

- [x] All required sections are complete
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Problem statement is specific and measurable
- [x] Every feature has testable acceptance criteria (Gherkin format)
- [x] No contradictions between sections

### QUALITY CHECKS (Should Pass)

- [x] Problem is validated by evidence (not assumptions)
- [x] Context → Problem → Solution flow makes sense
- [x] Every persona has at least one user journey
- [x] All MoSCoW categories addressed (Must/Should/Could/Won't)
- [x] Every metric has corresponding tracking events
- [x] No feature redundancy
- [x] No technical implementation details included
- [x] A new team member could understand this PRD

---

## Product Overview

### Vision

Give the advisor instant visibility into the health of every data ingestion job —
so stale or broken data never silently reaches a client presentation.

### Problem Statement

The India Investment Analyzer runs 6 scheduled background jobs that ingest
market data and compute scores. When any of these jobs fail today, there is
no indication in the UI. The advisor has no way to know:

- **Which job failed** and when it last ran successfully
- **Why it failed** (network error, bad data, schema change, etc.)
- **How stale the displayed data is** before a client meeting

The only recourse today is to access the server terminal and read raw logs —
a process that is slow, requires technical context, and breaks advisor workflow.
In practice this means bad or stale data can be presented to clients without
the advisor realising it.

The core pain: **jobs fail silently, and fixing them requires leaving the app**.

### Value Proposition

A single `/admin` page shows the full run history of every job — status,
duration, error message, and affected row counts — and lets the advisor
trigger a re-run with one click. A passive freshness bar on the main
dashboard gives an at-a-glance "all green" or "⚠ stale" signal before
every client session, without navigating away.

The advisor can diagnose a broken job, understand the cause, and fix it
entirely within the application, in under two minutes.

---

## User Personas

### Primary Persona: The Advisor (Arun)

- **Demographics:** Individual financial advisor, sole user of the application,
  high domain expertise in Indian investment products, moderate technical
  comfort (comfortable with a terminal but prefers not to rely on it for
  routine operations)
- **Goals:**
  - Know that data shown to clients is current and accurate before a meeting
  - Quickly identify and resolve ingestion failures without server access
  - Trust the system enough to use it confidently day-to-day
- **Pain Points:**
  - Jobs fail silently — no alert, no indication in the UI
  - Diagnosing a failure requires terminal access and log-reading
  - No way to re-run a failed job without a manual CLI command
  - The existing `DataFreshness` component exists in code but has never been
    wired up — even basic staleness warnings are invisible today

### Secondary Personas

None. This is a single-user application.

---

## User Journey Maps

### Primary User Journey: Morning Pre-Client Health Check

1. **Awareness:** Advisor opens the dashboard before a 9am client call and
   sees a red ⚠ indicator on the data freshness bar — AMFI data is 3 days old.
2. **Consideration:** Advisor navigates to `/admin` to understand what happened.
   The `ingest_amfi` card shows the last run failed at 23:30 the previous
   night with error: "Connection timeout".
3. **Adoption:** Advisor clicks "Run Now" on the `ingest_amfi` card. The
   button shows a spinner; the status badge flips to "Running".
4. **Usage:** After ~30 seconds the job completes, the history table gains a
   new "Success — 847 rows inserted" entry. The advisor returns to the
   dashboard; the freshness bar is now green.
5. **Retention:** Advisor checks `/admin` as part of their morning routine,
   replacing the need for any terminal access.

### Secondary User Journey: Diagnosing a Recurring Failure

1. Advisor notices the `ingest_equity` card has 4 consecutive failures in
   the last-10-runs table.
2. Advisor expands the error column — all 4 show "yfinance_empty ticker=^NSEI".
3. Advisor understands the upstream data source issue and investigates the
   ticker configuration, rather than assuming the scheduler is down.

---

## Feature Requirements

### Must Have Features

#### Feature 1: Job Run History per Job

- **User Story:** As the advisor, I want to see the last 10 runs for each
  ingestion job so that I can quickly understand whether a job is healthy
  and what went wrong if it failed.
- **Acceptance Criteria:**
  - [ ] Given the advisor opens `/admin`, When the page loads, Then one card
        is displayed for each of the 6 jobs (ingest_amfi, ingest_equity,
        ingest_nps, ingest_mfapi, compute_metrics, compute_scores).
  - [ ] Given a job has run at least once, When its card is viewed, Then the
        most recent run's status (Success / Failed / Running), timestamp,
        and duration are visible without expanding anything.
  - [ ] Given a job has failed at least once, When the advisor looks at its
        run history, Then the error message from that failure is visible in
        the history table row.
  - [ ] Given a job has never run, When its card is viewed, Then a "Never run"
        status badge is shown rather than an empty or broken state.
  - [ ] Given a job has run more than 10 times, When the history is shown,
        Then only the 10 most recent runs are displayed (oldest are not shown).
  - [ ] Given a job is currently running, When the card is viewed, Then its
        status badge shows "Running" with a visual indicator, And the Run Now
        button is disabled for that job.

#### Feature 2: Manual Job Trigger (Run Now)

- **User Story:** As the advisor, I want to re-run any job from the UI so
  that I can recover from a failure without needing terminal access.
- **Acceptance Criteria:**
  - [ ] Given a job is not currently running, When the advisor clicks "Run Now",
        Then the job begins executing and the status badge changes to "Running"
        within 2 seconds.
  - [ ] Given the advisor has clicked "Run Now", When the job is running, Then
        the "Run Now" button is disabled for that job, preventing double-execution.
  - [ ] Given a triggered job completes successfully, When it finishes, Then
        a new "Success" entry appears at the top of the run history table with
        rows affected count.
  - [ ] Given a triggered job fails, When it finishes, Then a new "Failed"
        entry appears at the top of the run history table with the error message.
  - [ ] Given one job is running, When the advisor views other job cards, Then
        their "Run Now" buttons remain enabled — only the running job is locked.

#### Feature 3: Data Freshness Bar on Main Dashboard

- **User Story:** As the advisor, I want a passive at-a-glance health signal
  on the main dashboard so that I notice stale data before a client session
  without navigating to a separate page.
- **Acceptance Criteria:**
  - [ ] Given the advisor opens `/dashboard`, When products load, Then a
        freshness bar is visible showing last-update dates for AMFI, Equity,
        and NPS data sources.
  - [ ] Given any data source has not been updated in more than 48 hours,
        When the freshness bar is shown, Then that source displays a red ⚠
        stale warning next to its date.
  - [ ] Given all data sources were updated within 48 hours, When the freshness
        bar is shown, Then no warning icons appear (all indicators are neutral/green).
  - [ ] Given data is loading, When products are being fetched, Then the
        freshness bar shows a loading state rather than empty dates.

#### Feature 4: /admin Page Access

- **User Story:** As the advisor, I want the admin page to be accessible by
  direct URL without appearing in the main navigation, so that the advisor
  workflow stays clean while the page remains reachable.
- **Acceptance Criteria:**
  - [ ] Given the advisor navigates to `/admin`, When they are authenticated,
        Then the page loads and displays all job cards.
  - [ ] Given the advisor is not authenticated, When they navigate to `/admin`,
        Then they are redirected to `/login`.
  - [ ] Given the advisor is on any page, When they look at the nav bar, Then
        no "Admin" or "System Health" link is visible in the main navigation.
  - [ ] Given the `/admin` route is accessed, When the page renders, Then it
        uses the same `AppNav` component as other pages (consistent nav +
        sign-out button).

### Should Have Features

- **Auto-refresh on /admin:** The page automatically refreshes job status
  every 30 seconds while open, so a triggered job's completion is reflected
  without a manual browser refresh.
- **Rows affected display:** Each successful run shows how many rows were
  inserted or updated, giving a quick sanity check (e.g. "0 rows inserted"
  on a nominally successful run is a warning signal).

### Could Have Features

- **Duration trend:** A small sparkline or trend arrow showing whether recent
  job durations are increasing (potential performance issue) vs. stable.
- **Keyboard shortcut to /admin:** A footer link or keyboard shortcut
  (e.g. `?` help menu) that reveals the `/admin` URL for discoverability.

### Won't Have (This Phase)

- **Email / push alerts on failure** — manual dashboard check is sufficient
- **In-app notification badge** — out of scope for V1
- **Job schedule editing from UI** — cron triggers stay in code
- **Raw log file streaming** — structured fields in the DB are sufficient
- **Data rollback after bad ingestion** — not needed for current data sources
- **Cancel a running job** — jobs complete quickly; abort adds complexity
- **Separate admin role / access control** — single-user app, JWT auth is enough
- **External monitoring integration** (Prometheus, Datadog, etc.)

---

## Detailed Feature Specifications

### Feature: Manual Job Trigger (Run Now)

**Description:** When the advisor clicks "Run Now" on a job card, the job
executes in the background (same execution path as the scheduler), and the
UI reflects the job's progress in near-real time.

**User Flow:**
1. Advisor sees a "Failed" badge on the `ingest_amfi` card.
2. Advisor clicks "Run Now".
3. Badge immediately changes to "Running"; button becomes disabled with a spinner.
4. The page polls for status updates every 5 seconds.
5. Job finishes (success or failure); badge updates; a new row appears at
   the top of the run history table.
6. "Run Now" button re-enables.

**Business Rules:**
- Rule 1: Only one instance of a given job may run at a time. If the scheduler
  fires a job and the advisor clicks "Run Now" for the same job within the
  same window, the manual trigger is rejected with a "Job already running"
  message — the job is not started twice.
- Rule 2: All 6 jobs must be triggerable via the UI, including the two
  compute jobs (compute_metrics, compute_scores), not just ingestion jobs.
- Rule 3: A triggered run is logged to the same job_runs history as a
  scheduled run, with the same fields. There is no distinction between
  "manual" and "scheduled" in the displayed history.
- Rule 4: The "Run Now" button is always enabled by default unless that
  specific job is currently in "Running" state.

**Edge Cases:**
- Job takes longer than expected (e.g. > 2 minutes) → UI continues showing
  "Running" badge; no timeout on the client side.
- Network error during status poll → UI shows last known state and continues
  polling; no crash.
- Job fails immediately with an exception → "Failed" badge appears; error
  message is stored and shown in the history row.
- Advisor closes the browser mid-run → Job continues executing on the server;
  result is recorded in history regardless.

---

## Success Metrics

### Key Performance Indicators

- **Adoption:** The advisor checks `/admin` at least 3 times per week within
  the first month of release (replacing terminal log checks).
- **Effectiveness:** Time-to-diagnose a job failure drops from ~10 minutes
  (terminal log reading) to under 2 minutes (UI inspection).
- **Quality:** Zero instances of stale data being presented to a client without
  a visible warning after this feature ships.
- **Trigger reliability:** "Run Now" successfully starts the intended job
  100% of the time when the job is not already running.

### Tracking Requirements

| Event | Properties | Purpose |
|-------|------------|---------|
| admin_page_opened | timestamp, source (direct_url / nav_link) | Measure adoption of daily check habit |
| job_run_now_clicked | job_name, previous_status | Measure which jobs fail most and are manually re-run |
| job_run_completed | job_name, status, duration_seconds, rows_affected | Validate reliability of trigger execution |
| freshness_warning_seen | source (amfi / equity / nps), hours_stale | Measure how often stale data would have reached clients |
| admin_page_viewed_after_warning | time_delta_seconds | Measure whether the freshness bar drives admin page visits |

---

## Constraints and Assumptions

### Constraints

- The application is a single-user, self-hosted app running locally — no
  multi-tenancy, no cloud deployment requirements.
- The backend uses FastAPI + SQLite + APScheduler; no new dependencies should
  be introduced unless strictly necessary.
- The frontend uses React + Zustand + TailwindCSS; the same stack applies.
- No external monitoring infrastructure (Prometheus, cloud logging) is
  available or required.

### Assumptions

- The advisor checks the dashboard on a machine where the backend server
  is running — `/admin` does not need to work when the server is down.
- A history of 10 runs per job is sufficient for day-to-day diagnostics;
  longer-term trend analysis is not needed.
- Job execution is fast enough (under 2 minutes for most jobs) that the
  advisor will wait on the page to see a result; async email notification
  is not required.
- The existing `DataFreshness` component in the frontend codebase is
  functionally correct and only needs to be wired up (not rewritten).
- All 6 jobs share the same execution model and can be wrapped uniformly
  to capture run history.

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| A manually triggered job runs concurrently with the scheduler, corrupting data | High | Medium | Check for "Running" status before starting; scheduler and manual trigger share the same lock/state check |
| Job history table grows unboundedly over time | Low | High | Automatically prune records older than 90 days or cap at 100 runs per job |
| "Run Now" UI appears to succeed but the job silently fails to start | High | Low | API returns an error response if the job cannot be started; UI surfaces this as an error message |
| Polling every 5s puts unnecessary load on the server | Low | Low | Only poll when `/admin` page is open and a job is in "Running" state; switch to 30s interval otherwise |

## Open Questions

None. All decisions confirmed with the user during brainstorm.

---

## Supporting Research

### Competitive Analysis

Job monitoring dashboards exist in tools like Apache Airflow (DAG run view),
Prefect, and Dagster. All share the same core pattern: one row/card per job,
colour-coded status, last-run timestamp, error surface, and manual re-trigger.
The key insight from these tools is that **error message visibility** is the
single most valuable field — without it, a "Failed" status is only marginally
better than no status at all. This informed the requirement to persist and
display the full error message, not just a pass/fail flag.

Celery Flower provides a useful precedent for the "running" state — showing
a spinner and disabling the trigger button prevents user confusion about
whether their action registered.

For this application, all of these tools are far too heavy. The design
intentionally mirrors their UX patterns at a fraction of the complexity.

### User Research

Validated directly with the sole user (Arun) during brainstorm session on
2026-03-08. Key findings:
- Primary need: diagnose failures (not just detect them)
- Manual trigger is critical, not optional
- Full run history (last 10) preferred over single latest status
- `/admin` placement preferred to keep advisor workflow clean
- Freshness bar on main dashboard approved for passive monitoring

### Market Data

Not applicable — this is an internal tool for a single-user application,
not a market-facing product.
