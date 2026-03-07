---
title: "Phase 2: Data Ingestion Layer"
status: completed
version: "1.0"
phase: 2
---

# Phase 2: Data Ingestion Layer

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/External Interfaces; outbound]` — AMFI, mfapi.in, yfinance, NPSTRUST interfaces
- `[ref: SDD/Implementation Examples; AMFI NAV Ingestion]` — Parser implementation guidance
- `[ref: SDD/Directory Map; backend/app/jobs/]` — Job file locations
- `[ref: SDD/Runtime View; Error Handling; AMFI API down]` — Stale data fallback behavior

**Key Decisions**:
- All external API calls happen in background jobs only — never during user requests (ADR-3 consequence)
- Data freshness timestamps per source must be stored and returned with product queries
- Parser must be tolerant of AMFI format irregularities (category header rows interspersed)

**Dependencies**:
- Phase 1 complete (DB schema, `nav_history`, `index_history`, `mutual_funds`, `asset_classes` tables exist)

---

## Tasks

Implements all external data ingestion pipelines, populating the database with historical and current market data required by the analytics engine.

- [x] **T2.1 AMFI NAV daily ingestion job** `[activity: backend-data]`

  1. Prime: Read `[ref: SDD/External Interfaces; AMFI NAV Feed]` and `[ref: SDD/Implementation Examples; AMFI NAV Ingestion]`
  2. Test: Given a sample AMFI text fixture (20 lines including 2 category headers and 1 malformed row), assert: parser returns 17 valid records; malformed rows are skipped; scheme codes are integers; NAV is a positive float; date parsed as `datetime.date`; existing `nav_history` rows are not duplicated on re-run
  3. Implement: Create `app/jobs/ingest_amfi.py` with `fetch_amfi_nav()` (HTTP GET AMFI URL), `parse_amfi_nav(raw_text)` (pipe-delimiter parser per SDD example), `upsert_nav_history(records, session)` (INSERT OR IGNORE for existing date+scheme combos), `run()` entry point; update `data_freshness` table or equivalent metadata row after successful run
  4. Validate: Run against live AMFI URL (or VCR-recorded fixture); assert ≥ 1500 records inserted; assert no duplicates; assert `nav_history` count increases on second run only for new dates
  5. Success:
    - [ ] Parser handles interspersed category header rows without error `[ref: SDD/Implementation Gotchas; AMFI text format fragility]`
    - [ ] Failed rows are logged with row content but do not abort the full ingestion `[ref: SDD/Error Handling; AMFI API down]`
    - [ ] Job is idempotent — running twice on the same day does not create duplicate rows `[ref: SDD/Data Storage Schema; nav_history PRIMARY KEY]`

- [x] **T2.2 mfapi.in historical NAV backfill job** `[activity: backend-data]`

  1. Prime: Read `[ref: SDD/External Interfaces; mfapi.in Historical NAV]` — endpoint: `https://www.mfapi.in/mf/{scheme_code}`
  2. Test: Given a mock mfapi.in response for scheme code 119551 with 1000 historical NAV rows, assert: all rows inserted into `nav_history`; dates parsed correctly; NAV values are floats; scheme already in `mutual_funds` table before backfill runs (backfill does not create new schemes)
  3. Implement: Create `app/jobs/ingest_mfapi.py` with `backfill_historical_nav(scheme_code, session)`, batch processing (fetch one scheme at a time with 0.5s delay to avoid rate limiting), `backfill_all_schemes(session)` that iterates all active `mutual_funds` rows, progress logging every 100 schemes
  4. Validate: Run backfill on 10 scheme codes (from seeded `mutual_funds`); assert `nav_history` has ≥ 10×250 rows (≥ 1 year of data per fund); assert no `scheme_code` in `nav_history` that is not in `mutual_funds`
  5. Success:
    - [ ] Historical NAV data available for at least 5 years for schemes with ≥ 5-year history `[ref: SDD/Complex Logic; compute_metrics algorithm]`
    - [ ] Rate limiting handled: HTTP 429 triggers 60s backoff and retry `[ref: SDD/Error Handling; mfapi.in rate limit]`

- [x] **T2.3 yfinance NSE index data ingestion** `[activity: backend-data]` `[parallel: true]`

  1. Prime: Read `[ref: SDD/External Interfaces; yfinance NSE/BSE Data]` — tickers: `^NSEI` (Nifty 50), `^BSESN` (Sensex), `^NSMIDCP` (Nifty Midcap), `GOLDBEES.NS` (Gold ETF proxy), `EMBASSY.NS` (REIT proxy)
  2. Test: Given a mocked yfinance response for `^NSEI` with 1000 rows, assert: data inserted into `index_history` with correct ticker, date, close_price; dates are trading days only (no weekends); job is idempotent; unknown ticker returns graceful error (logged, not raised)
  3. Implement: Create `app/jobs/ingest_equity.py` with `fetch_index_history(ticker, period='10y')` using yfinance, `upsert_index_history(ticker, df, session)`, `run()` iterating over all configured index tickers; store ticker-to-asset_class mapping in `data/reference/index_tickers.json`
  4. Validate: Run live (or VCR fixture); assert `index_history` has Nifty 50 data going back ≥ 5 years; assert close prices are positive; assert row count increases by 1 on next trading day run
  5. Success:
    - [ ] `index_history` populated for all 5+ index tickers `[ref: SDD/Data Storage Schema; index_history]`
    - [ ] Non-trading day gaps (weekends, holidays) do not create null rows `[ref: SDD/Complex Logic; compute_metrics]`

- [x] **T2.4 NPSTRUST weekly NPS returns ingestion** `[activity: backend-data]` `[parallel: true]`

  1. Prime: Read `[ref: SDD/External Interfaces; NPSTRUST Returns]` — weekly HTML table at NPSTRUST site; 7 Pension Fund Managers × 4 schemes
  2. Test: Given an HTML fixture of NPSTRUST returns table, assert: correct PFM name, scheme type (Equity/G-Bond/Corp-Bond), 1Y/3Y/5Y returns extracted as floats; missing return (e.g., scheme < 1 year old) stored as NULL; job is idempotent
  3. Implement: Create `app/jobs/ingest_nps.py` with HTML parser using `html.parser` or BeautifulSoup, NPS return rows mapped to `index_history` table using NPS-specific ticker keys (e.g., `NPS_SBI_EQUITY`), weekly scheduler entry in `app/jobs/scheduler.py`
  4. Validate: Run against saved HTML fixture; assert returns loaded for SBI Pension Fund Equity scheme; assert stored values match fixture values exactly (float precision); assert weekly re-run updates existing rows with latest data
  5. Success:
    - [ ] NPS Tier 1 returns (1Y, 3Y, 5Y) available for all 7 PFMs × 4 schemes `[ref: PRD/Feature 1 AC; NPS in dashboard]`
    - [ ] Scrape failure (HTML format changed) logs error and retains previous week's data without crashing `[ref: SDD/Technical Debt; NPSTRUST data format]`

- [x] **T2.5 APScheduler setup + manual fund catalog seeding** `[activity: backend-infrastructure]`

  1. Prime: Read `[ref: SDD/Directory Map; app/jobs/scheduler.py]` and `[ref: SDD/Deployment View; Dependencies]`
  2. Test: Assert APScheduler starts when FastAPI app starts; assert AMFI job is registered for 23:30 IST daily; assert NPS job is registered for Monday 07:00 IST; assert equity job is registered for 16:30 IST on weekdays; running scheduler.run_job('ingest_amfi') manually succeeds
  3. Implement: Create `app/jobs/scheduler.py` registering all 4 ingestion jobs + nightly compute_metrics job (Phase 3) with APScheduler cron triggers; start scheduler in `app/main.py` lifespan; create `app/jobs/seed_fund_catalog.py` that fetches the full AMFI scheme list (one-time) and populates `mutual_funds` with scheme_code, scheme_name, amfi_category — seeding ~2000 fund rows
  4. Validate: Start FastAPI app; assert scheduler shows 5 registered jobs; manually trigger `ingest_amfi` via `python -m app.jobs.ingest_amfi`; confirm job runs and returns without unhandled exceptions
  5. Success:
    - [ ] All 5 scheduled jobs registered with correct cron schedules `[ref: SDD/External Interfaces; schedule fields]`
    - [ ] `mutual_funds` table has ≥ 1500 active schemes after catalog seeding `[ref: SDD/Data Storage Schema; mutual_funds]`

- [x] **T2.6 Phase 2 Validation** `[activity: validate]`

  - Run `pytest tests/unit/test_ingestion.py` and `pytest tests/integration/test_data_jobs.py`. Assert `nav_history`, `index_history` row counts are non-zero. Assert all 5 scheduler jobs are registered. Run `python -m app.jobs.compute_metrics` (stub from Phase 3) — confirm it at least starts without import errors.

---

**Phase 2 Exit Criteria**: All 4 data sources ingested; `nav_history` has ≥ 5 years of data for top 50 mutual funds; `index_history` has Nifty 50, gold ETF, REIT proxy data; NPS returns loaded; APScheduler configured.
