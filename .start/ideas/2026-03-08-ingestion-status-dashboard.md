# Design: Ingestion Status Dashboard
Date: 2026-03-08

## Problem
Ingestion jobs fail silently. The advisor has no visibility into what failed,
when, or why without accessing the server directly.

## User
Advisor (single user, same person who runs the app).

## Core Pain Point
Diagnose when something breaks — need to see what failed, the error message,
and be able to trigger a re-run without touching the terminal.

## Approach
Persistent job run history table + hidden /admin page.

## What Gets Built

### Backend
- `job_runs` table: job_name, started_at, finished_at, status
  (running | success | failed), rows_affected, error_msg
- All 6 jobs wrapped to write a record on every execution
- `GET  /api/admin/jobs`                  — history per job (last 10 runs each)
- `POST /api/admin/jobs/{job_name}/run`   — manual trigger

### Jobs covered
- ingest_amfi        (daily 23:30)
- ingest_equity      (weekdays 16:30)
- ingest_nps         (Monday 07:00)
- ingest_mfapi       (Sunday 02:00)
- compute_metrics    (daily 01:00)
- compute_scores     (daily 00:00)

### Frontend — /admin page
- One card per job
- Status badge: Running / Success / Failed / Never run
- Last run time + duration
- "Run Now" button (disables while running, no double-execution)
- Collapsible table: last 10 runs with timestamp, status, duration,
  rows affected, error message
- Auto-refreshes every 30 seconds
- Accessible via direct URL only — not in main nav
- Protected by existing JWT auth (no separate admin role)

### Frontend — /dashboard freshness bar
- Wire up the already-built DataFreshness component (exists but not integrated)
- Three indicators: AMFI / Equity / NPS with last-update date
- Red warning if any source is stale (>48h)
- Passive signal before client meetings

## Out of Scope
- Email / push alerts on failure
- Multi-user admin role separation
- Raw log file streaming
- Job schedule editing from UI
- Data rollback after bad ingestion
- Cancel running job
