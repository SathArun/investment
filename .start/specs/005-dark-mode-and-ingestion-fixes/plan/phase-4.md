---
title: "Phase 4: NPS Data Source Fix"
status: completed
version: "1.0"
phase: 4
---

# Phase 4: NPS Data Source Fix

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/NPS Fix — New Data Source Strategy]` — two-path strategy, Path A endpoint, Path B seed format
- `[ref: SDD/Runtime View — NPS Returns Ingestion]` — sequence diagram
- `[ref: PRD/Feature 4 — NPS Returns — Weekly Data Availability]` — acceptance criteria
- `[ref: SDD/Glossary — IndexHistory]` — `ticker`, `price_date`, `close_price` schema

**Key Decisions**:
- ADR-3: Two-path — Path A (direct JSON from NPS Trust API, discovered via network tab); Path B (static `nps_returns_seed.json`).
- Existing `upsert_nps_returns()`, `make_nps_ticker()`, `PFM_NAMES`, `SCHEME_TYPES`, `RETURN_HORIZONS` are reused by both paths.
- On any failure, previous `IndexHistory` records are retained (no delete).
- Path A endpoint URL must be confirmed via browser network tab inspection before T4.1.

**Dependencies**:
- None. Independent of Phases 1, 2, and 3.

**Pre-task investigation (not a tracked task):**
Before T4.1, open Chrome DevTools → Network tab on `https://www.npstrust.org.in/weekly-snapshot-nps-schemes`. Filter for XHR/Fetch requests while the page loads. Look for a JSON response containing return percentage values. Record the URL, method, and any required headers/cookies. This determines whether Path A is viable.

---

## Tasks

Delivers a working NPS ingestion job that produces ≥15 IndexHistory records (5 PFMs × 3 horizons) for at least Equity, GBOND, and CORPBOND schemes — either from a live JSON endpoint (Path A) or a maintained static seed file (Path B).

---

- [ ] **T4.1 Create NPS seed file (Path B fallback)** `[activity: backend-api]`

  1. **Prime**: Read `backend/app/jobs/ingest_nps.py`, focusing on `make_nps_ticker()`, `PFM_NAMES`, `SCHEME_TYPES`, `RETURN_HORIZONS`, and `upsert_nps_returns()`. Review SDD seed format `[ref: SDD/NPS Fix — New Data Source Strategy]`.
  2. **Test**: Write a test asserting that loading `nps_returns_seed.json` and passing parsed records to `upsert_nps_returns()` inserts ≥15 `IndexHistory` rows (5 PFMs × 3 horizons for Equity + GBOND + CORPBOND).
  3. **Implement**: Create `backend/data/reference/nps_returns_seed.json` with the structure:
     ```json
     {
       "as_of_date": "YYYY-MM-DD",
       "records": [
         {"pfm": "SBI",  "scheme": "EQUITY",   "1Y": 0.xxxx, "3Y": 0.xxxx, "5Y": 0.xxxx},
         {"pfm": "SBI",  "scheme": "GBOND",    "1Y": 0.xxxx, "3Y": 0.xxxx, "5Y": 0.xxxx},
         {"pfm": "SBI",  "scheme": "CORPBOND", "1Y": 0.xxxx, "3Y": 0.xxxx, "5Y": 0.xxxx},
         ... (repeat for LIC, UTI, HDFC, KOTAK)
       ]
     }
     ```
     Populate with current NPS return data (source: PFRDA / NPS Trust published tables). Values must be decimal fractions (e.g., `0.1552` for 15.52%). `as_of_date` must be within the last 30 days.

     Also implement `load_nps_seed() -> list[dict]` helper function in `ingest_nps.py` that reads this file, converts each record into the `{ticker, price_date, close_price}` format expected by `upsert_nps_returns()`, using `make_nps_ticker(pfm, scheme, horizon)` for the ticker.
  4. **Validate**: `pytest tests/ -k nps_seed` passes. Seed file is valid JSON. `load_nps_seed()` produces ≥15 records.
  5. **Success**: `load_nps_seed()` returns ≥15 records covering 5 PFMs × Equity/GBOND/CORPBOND × 3 horizons. `[ref: PRD/AC-4.1]`

---

- [ ] **T4.2 Implement two-path `fetch_nps_data()` replacing `fetch_nps_html()`** `[activity: backend-api]`

  1. **Prime**: Re-read `ingest_nps.py` `fetch_nps_html()` and `run()`. Review SDD two-path strategy `[ref: SDD/NPS Fix — New Data Source Strategy]`. Confirm Path A endpoint URL from the network tab investigation (pre-task investigation above).
  2. **Test**: Write tests asserting:
     - When Path A (JSON endpoint) returns valid data, `fetch_nps_data()` returns parsed records and does NOT call `load_nps_seed()`.
     - When Path A raises an exception, `fetch_nps_data()` falls through to `load_nps_seed()` (Path B) and returns seed records.
     - `run()` never raises an exception — on total failure, it logs and returns 0.
  3. **Implement**:
     - **If Path A endpoint found**: Add `NPS_JSON_URL` constant with the discovered endpoint. Implement `fetch_nps_json() -> list[dict]` that GETs the endpoint with a `User-Agent` header, parses the JSON, and returns records in `{ticker, price_date, close_price}` format.
     - **If Path A not viable**: Skip `fetch_nps_json()` — Path B is the sole path.
     - Replace `fetch_nps_html()` with `fetch_nps_data() -> list[dict]`:
       ```python
       def fetch_nps_data() -> list[dict]:
           try:
               records = fetch_nps_json()   # Path A (omit if not viable)
               if records:
                   logger.info("nps_path_a_success", count=len(records))
                   return records
           except Exception as e:
               logger.warning("nps_path_a_failed", error=str(e))
           logger.info("nps_path_b_seed_fallback")
           return load_nps_seed()
       ```
     - Update `run()` to call `fetch_nps_data()` instead of `fetch_nps_html()` + `parse_nps_html()`.
     - Keep `parse_nps_html()` in the file (it may still be called if Path A returns raw HTML unexpectedly), but it is no longer the primary path.
  4. **Validate**: `pytest tests/ -k nps` all pass. Run `python -m app.jobs.ingest_nps` — check `nps_job_complete` log with `inserted + updated >= 15`.
  5. **Success**:
     - Job produces ≥15 IndexHistory records for 5 PFMs. `[ref: PRD/AC-4.1]`
     - On Path A failure, seed is used — previous records retained. `[ref: PRD/AC-4.2]`
     - Seed data is ≤30 days stale. `[ref: PRD/AC-4.3]`

---

- [ ] **T4.3 Phase 4 Validation** `[activity: validate]`

  Run `pytest tests/ -k nps` from `backend/`. All must pass.

  Manual integration check:
  - [ ] `python -m app.jobs.ingest_nps` completes without raising.
  - [ ] Structlog output shows `nps_job_complete` with `inserted + updated >= 15`.
  - [ ] Re-running the job updates existing records (upsert — no duplicates, `updated` count increases).
  - [ ] If Path A is implemented: temporarily break the URL and confirm fallback to seed with `nps_path_b_seed_fallback` log line.

  Success: NPS job reliably produces ≥15 IndexHistory records per run via seed or live endpoint. `[ref: PRD/AC-4.1, AC-4.2, AC-4.3]`
