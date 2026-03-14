---
title: "Phase 2: AMFI Ingestion Fix"
status: completed
version: "1.0"
phase: 2
---

# Phase 2: AMFI Ingestion Fix

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/AMFI Fix — User-Agent Header]` — exact header dict and fetch call change
- `[ref: SDD/Runtime View — AMFI NAV Ingestion]` — sequence diagram
- `[ref: PRD/Feature 2 — AMFI NAV Ingestion — Reliable Daily Update]` — acceptance criteria

**Key Decisions**:
- ADR-5: No shared retry utility — AMFI keeps its own retry logic (single URL, `raise_for_status`).
- Root cause: `requests.get(AMFI_URL, timeout=30)` with no `User-Agent` is blocked by AMFI's CDN (Akamai).
- The two-pass upsert (flush MutualFund rows before NavHistory) must not be disturbed.

**Dependencies**:
- None. Independent of Phases 1, 3, and 4.

---

## Tasks

Delivers a working AMFI ingestion job that inserts ≥1,000 NAV records per run by adding the missing browser User-Agent header.

---

- [ ] **T2.1 Add User-Agent header to AMFI fetch** `[activity: backend-api]`

  1. **Prime**: Read `backend/app/jobs/ingest_amfi.py`, focusing on `fetch_amfi_nav()`. Review SDD AMFI fix spec `[ref: SDD/AMFI Fix — User-Agent Header]`.
  2. **Test**: Write/update a test in `backend/tests/` that mocks `requests.get` and asserts:
     - The call includes `headers` with a `User-Agent` key containing `"Mozilla"`.
     - `fetch_amfi_nav()` returns the mocked response text on HTTP 200.
     - `fetch_amfi_nav()` raises on HTTP 4xx/5xx (existing behaviour preserved).
  3. **Implement**: In `ingest_amfi.py`:
     - Add module-level `AMFI_HEADERS` dict with `User-Agent`, `Accept`, and `Accept-Encoding` keys (see SDD for exact values).
     - Change `requests.get(AMFI_URL, timeout=30)` → `requests.get(AMFI_URL, timeout=30, headers=AMFI_HEADERS)`.
     - No other changes to `parse_amfi_nav()` or `upsert_nav_history()`.
  4. **Validate**: `pytest tests/ -k amfi` passes. Run `python -m app.jobs.ingest_amfi` manually — check logs for `amfi_job_complete` with `inserted > 0`.
  5. **Success**:
     - HTTP request to AMFI includes `User-Agent` header. `[ref: SDD/AC — AMFI: HTTP request includes User-Agent]`
     - Manual run inserts or skips ≥1,000 NavHistory rows. `[ref: PRD/AC-2.1]`
     - Job failure (e.g., network error) logs `amfi_job_failed` and re-raises — scheduler error handling unchanged. `[ref: PRD/AC-2.2]`

---

- [ ] **T2.2 Phase 2 Validation** `[activity: validate]`

  Run `pytest tests/ -k amfi` from `backend/`. All must pass.

  Manual integration check:
  - [ ] `python -m app.jobs.ingest_amfi` completes without exception.
  - [ ] Structlog output shows `amfi_job_complete` with `inserted >= 1` (or `skipped >= 1000` if today's NAVs already loaded).
  - [ ] No regression: `parse_amfi_nav` and `upsert_nav_history` logic unchanged.

  Success: AMFI job runs to completion and produces non-zero row count. `[ref: PRD/AC-2.1]`
