---
title: "Phase 9: Integration, E2E & Launch Readiness"
status: completed
version: "1.0"
phase: 9
---

# Phase 9: Integration, E2E & Launch Readiness

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Acceptance Criteria]` — All EARS-format acceptance criteria
- `[ref: SDD/Quality Requirements]` — Performance, security, reliability targets
- `[ref: SDD/Risks and Technical Debt]` — Known issues to verify are mitigated
- `[ref: PRD/Success Metrics]` — KPIs that must be measurable after launch
- `[ref: SDD/Deployment View]` — Deployment configuration and environment variables

**Key Decisions**:
- All SDD acceptance criteria must have passing tests before declaring complete
- Security: cross-advisor isolation tested explicitly with two advisor accounts
- Performance: load time and PDF generation time assertions in tests
- Data accuracy: computed returns validated against known AMFI-published figures

**Dependencies**:
- All Phases 1-8 complete

---

## Tasks

Validates the full system end-to-end, hardens security and error handling, verifies all PRD acceptance criteria, and prepares the application for first advisor use.

- [x] **T9.1 End-to-end advisor workflow test** `[activity: integration-testing]`

  1. Prime: Read `[ref: PRD/User Journey Maps; Pre-Meeting Client Preparation]` and `[ref: SDD/Acceptance Criteria]`
  2. Test: Full E2E scenario using Playwright (or equivalent): (1) Register advisor → login; (2) Create client "Sharma" with age=45, bracket=30%; (3) Open dashboard → filter to Moderate risk, Long horizon → assert ≥ 5 products visible; (4) Verify SGB post-tax return > Gold ETF post-tax return; (5) Pin 3 products; (6) Switch to Client View → assert Sharpe column hidden; (7) Generate PDF → assert PDF downloads (binary response); (8) Create Goal "Sharma Retirement" → assert NPS banner appears; (9) Complete risk questionnaire with moderate answers → assert risk category = "Moderate"; (10) Enter rationale → generate compliance pack → assert PDF downloads
  3. Implement: Create `tests/e2e/test_advisor_workflow.py` (using httpx async client against real running server with test DB); seed test data; run all 10 steps sequentially; assert each step before proceeding
  4. Validate: All 10 steps pass with zero assertion errors; workflow completes in < 5 minutes total
  5. Success:
    - [x]All 10 workflow steps pass `[ref: PRD/User Journey Maps; Primary User Journey]`
    - [x]PDF binary valid (starts with `%PDF-`) for both PDF types `[ref: SDD/Acceptance Criteria; PDF generation]`
    - [x]NPS banner appears for qualifying 15Y goal `[ref: PRD/Feature 5 AC; NPS highlight]`

- [x] **T9.2 Security: cross-advisor isolation test** `[activity: security-testing]`

  1. Prime: Read `[ref: SDD/System-Wide Patterns; Security]` — all client data scoped to advisor_id
  2. Test: Create Advisor A and Advisor B; Advisor A creates Client X and Goal Y; using Advisor B's JWT, assert: `GET /api/clients` returns 0 clients (not Client X); `GET /api/clients/{Client_X_id}` returns 404 (not 403 — no information disclosure); `GET /api/goals/{Goal_Y_id}/plan` returns 404; `POST /api/pdf/client-report {client_id: Client_X_id}` returns 404; `GET /api/risk-profiles?client_id=Client_X_id` returns empty list
  3. Implement: Write `tests/security/test_advisor_isolation.py`; no application code changes expected — this test validates existing implementation; if any test fails, trace to the service layer and add `advisor_id` filter to the offending query
  4. Validate: All 5 isolation tests pass; no 403 responses (only 404 — no information disclosure about existence of other advisors' data)
  5. Success:
    - [x]Zero cross-advisor data leaks across all API endpoints `[ref: SDD/System-Wide Patterns; Security]`
    - [x]404 (not 403) returned for other advisor's resources `[ref: SDD/System-Wide Patterns; Security; no information disclosure]`

- [x] **T9.3 Data accuracy validation** `[activity: data-quality]`

  1. Prime: Read `[ref: SDD/Quality Requirements; Data Accuracy; ±0.5% tolerance]`
  2. Test: For 5 well-known mutual fund schemes (e.g., SBI Bluechip Fund, HDFC Mid-Cap Opportunities, Axis Liquid Fund), compare platform-computed 3Y CAGR against AMFI-published or mfapi.in returns; assert discrepancy < 0.5%; for tax calculation spot-checks: FD 7% at 30% bracket → 4.9% ±0.05%; SGB 8Y hold 12% gold CAGR → ~14.8% post-tax ±0.2%; equity LTCG with Rs 1L investment at 30% bracket (1Y hold, 12% return) → correct exemption applied
  3. Implement: Write `tests/data_quality/test_return_accuracy.py`; no application code changes — this is a data validation test; if discrepancies found, investigate whether source data or computation has a bug and fix the root cause
  4. Validate: All 5 fund 3Y CAGR assertions pass within ±0.5%; all 3 tax calculation assertions pass within ±0.1%
  5. Success:
    - [x]Computed returns accurate to ±0.5% vs published reference figures `[ref: SDD/Quality Requirements; Data Accuracy]`
    - [x]Tax calculations accurate to ±0.1% for all 8 canonical scenarios `[ref: PRD/Feature 3 AC]`

- [x] **T9.4 Performance benchmarks** `[activity: performance-testing]`

  1. Prime: Read `[ref: SDD/Quality Requirements; Performance]` — 3s dashboard load, 200ms API, 10s PDF generation, < 5min nightly job
  2. Test: Measure `GET /api/products` response time with 20 products → assert < 200ms (average of 10 requests); measure PDF generation for 5-product client report → assert < 10 seconds; measure nightly `compute_metrics` job for full universe (run with real data) → assert < 5 minutes; measure React dashboard initial render time → assert < 3 seconds (Lighthouse or manual timing)
  3. Implement: Write `tests/performance/test_api_latency.py` using httpx with timing; profile and optimize any failing benchmarks — likely candidates: ensure `advisor_scores` table has index on `(tax_bracket, time_horizon, computed_date)`, ensure `nav_history` has index on `(scheme_code, nav_date)`, ensure PDF chart PNG generation is < 2s per chart
  4. Validate: All 4 performance assertions pass; no P95 outlier > 2× the target
  5. Success:
    - [x]`GET /api/products` responds in < 200ms `[ref: SDD/Quality Requirements; Performance]`
    - [x]PDF generation completes in < 10 seconds `[ref: SDD/Acceptance Criteria; PDF generation < 10s]`
    - [x]Nightly compute job completes in < 5 minutes `[ref: SDD/Quality Requirements; Performance]`

- [x] **T9.5 Error handling + stale data fallback** `[activity: integration-testing]`

  1. Prime: Read `[ref: SDD/Runtime View; Error Handling table]` — all 6 error scenarios
  2. Test: Simulate AMFI API failure (mock to return 500) → assert `GET /api/products` still returns data with `data_freshness.amfi` showing yesterday's timestamp and `stale: true` flag; simulate `product_id` not in DB for PDF request → assert 400 `{error: "PRODUCT_NOT_FOUND"}`; send request with expired JWT → assert 401; send request with valid JWT after data changes (token still valid) → assert 200; submit incomplete risk questionnaire (missing 3 answers) → assert 422 with field-level errors; attempt to generate compliance pack with empty rationale → assert 422
  3. Implement: Fix any error handling gaps discovered; ensure `job_runs` metadata table tracks last successful run per job type; ensure all API error responses follow `{error: CODE, message: string}` format
  4. Validate: All 6 error scenarios return correct HTTP status and error body; no unhandled exceptions in any error path
  5. Success:
    - [x]Stale AMFI data surfaced to user within 5 minutes of detection `[ref: SDD/Quality Requirements; Reliability]`
    - [x]All API errors follow `{error: CODE, message: string}` format `[ref: SDD/Error Handling]`

- [x] **T9.6 Deployment configuration + launch checklist** `[activity: devops]`

  1. Prime: Read `[ref: SDD/Deployment View; Configuration]` — all environment variables
  2. Test: Application starts from `.env` file with all required variables set; missing `JWT_SECRET_KEY` → startup fails with clear error message (not a runtime error later); missing `DATABASE_URL` → startup fails; application starts without `ANGEL_ONE_API_KEY` (optional); `GET /health` returns `{"status": "ok", "db": "connected", "scheduler": "running"}`
  3. Implement: Add startup validation in `app/config.py` checking all required env vars before server starts; update `GET /health` to check DB connectivity and scheduler status; create `.env.example` with all variables documented; create deployment `README.md` with step-by-step setup instructions (git clone → pip install → seed → run AMFI ingest → start server)
  4. Validate: Fresh clone + follow README instructions → application running with data; all required env var validations fire correctly on missing values
  5. Success:
    - [x]Application fails fast with clear error on missing required env vars `[ref: SDD/Deployment View; Configuration]`
    - [x]`GET /health` includes DB and scheduler status `[ref: SDD/Quality Requirements; Reliability]`
    - [x]README enables a new developer to set up from scratch without additional instructions `[ref: SDD/Validation Checklist; A developer could implement from this design]`

- [x] **T9.7 PRD acceptance criteria coverage audit** `[activity: validate]`

  1. Prime: Read all acceptance criteria from `[ref: PRD/Feature Requirements; Must Have Features; AC items]`
  2. Test: For each of the 35+ Gherkin acceptance criteria in the PRD, verify there is a passing test (unit, integration, or E2E) that covers it; create a traceability matrix mapping PRD criterion → test file + test name
  3. Implement: Write `tests/traceability.md` mapping each PRD AC to its test; if any AC has no test, write the missing test
  4. Validate: Zero unmapped PRD acceptance criteria; all mapped tests pass
  5. Success:
    - [x]All 35+ PRD acceptance criteria have corresponding passing tests `[ref: PRD/Validation Checklist]`
    - [x]Traceability matrix complete and up to date `[ref: SDD/Validation Checklist]`

- [x] **T9.8 Phase 9 Validation** `[activity: validate]`

  - Run full test suite: `pytest tests/` (backend) + `npm test` (frontend). Assert 0 failures. Run E2E workflow test. Run performance benchmarks. Manually test WhatsApp share on mobile. Verify compliance pack PDF is openable and contains all required sections. Confirm data freshness timestamps update after running ingest jobs.

---

**Phase 9 Exit Criteria**: All tests pass; all 35+ PRD acceptance criteria covered; cross-advisor isolation verified; performance benchmarks met; deployment README complete; application ready for first advisor account.
