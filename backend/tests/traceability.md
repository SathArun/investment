# PRD Acceptance Criteria — Test Traceability Audit

## Coverage Summary

| Metric | Count |
|--------|-------|
| Total Acceptance Criteria | 37 |
| Mapped to Tests | 37 |
| Unmapped ACs | 0 |

All 37 acceptance criteria (Must-Have Features: 30, Should-Have: 5, Cross-Cutting: 5 — plus Should-Have counted separately below) are covered by at least one test. Three real-data tests are skipped in CI until AMFI data is seeded; all other tests run in CI.

---

## Feature 1: Multi-Asset Dashboard

| AC ID | Acceptance Criterion | Test(s) | Status |
|-------|----------------------|---------|--------|
| AC1.1 | Dashboard shows >= 12 asset classes | `tests/integration/test_market_data_api.py::test_products_returns_sorted_list` | Mapped |
| AC1.2 | Sorting by any column works without API call | `frontend/src/tests/AssetTable.test.tsx` | Mapped |
| AC1.3 | Hover tooltip shows 10 required fields | `frontend/src/tests/AssetTable.test.tsx::hover tooltip shows extra fields` | Mapped |
| AC1.4 | Data freshness timestamps shown | `tests/integration/test_market_data_api.py` | Mapped |

---

## Feature 2: Composite Advisor Score

| AC ID | Acceptance Criterion | Test(s) | Status |
|-------|----------------------|---------|--------|
| AC2.1 | Score in range [0, 100] | `tests/unit/test_score_engine.py` | Mapped |
| AC2.2 | Score breakdown shows 6 sub-scores | `frontend/src/tests/AssetTable.test.tsx` | Mapped |
| AC2.3 | PPF consistency score = 100 | `tests/unit/test_score_engine.py` | Mapped |
| AC2.4 | NPS liquidity score = 10 | `tests/unit/test_score_engine.py` | Mapped |

---

## Feature 3: Tax Overlay Engine

| AC ID | Acceptance Criterion | Test(s) | Status |
|-------|----------------------|---------|--------|
| AC3.1 | FD 30% bracket -> ~4.9% post-tax | `tests/data_quality/test_return_accuracy.py::test_fd_30pct_bracket_accuracy` | Mapped |
| AC3.2 | PPF EEE -> no tax | `tests/data_quality/test_return_accuracy.py::test_ppf_eet_returns` | Mapped |
| AC3.3 | SGB maturity exempt | `tests/data_quality/test_return_accuracy.py::test_sgb_8y_maturity_tax_free` | Mapped |
| AC3.4 | Tax bracket banner visible in UI | `frontend/src/tests/FilterBar.test.tsx::banner visible when taxBracket > 0` | Mapped |

---

## Feature 4: Client Presentation Mode

| AC ID | Acceptance Criterion | Test(s) | Status |
|-------|----------------------|---------|--------|
| AC4.1 | Client view hides Sharpe | `frontend/src/tests/AssetTable.test.tsx::client view hides score breakdown button`; `frontend/src/tests/ClientView.test.tsx` | Mapped |
| AC4.2 | PDF generated with client info | `tests/integration/test_pdf_generation.py` | Mapped |
| AC4.3 | SEBI disclaimer in every PDF | `tests/integration/test_pdf_generation.py::test_sebi_disclaimer_in_client_report` | Mapped |
| AC4.4 | WhatsApp share link correct format | `frontend/src/tests/ClientView.test.tsx::constructs correct wa.me URL` | Mapped |
| AC4.5 | Max 5 products in PDF | `tests/integration/test_pdf_generation.py`; `frontend/src/tests/ClientView.test.tsx::validation error when > 5 products` | Mapped |

---

## Feature 5: Goal-Based Planner

| AC ID | Acceptance Criterion | Test(s) | Status |
|-------|----------------------|---------|--------|
| AC5.1 | Inflation-adjusted target shown | `tests/integration/test_goals.py` | Mapped |
| AC5.2 | NPS highlight for 15Y+, 20%+ bracket | `tests/integration/test_goals.py` | Mapped |
| AC5.3 | Step-up SIP corpus projection | `frontend/src/tests/GoalPlanner.test.tsx` | Mapped |
| AC5.4 | 3 scenario projections (conservative/base/optimistic) | `frontend/src/tests/GoalPlanner.test.tsx::corpus projection chart renders 3 lines` | Mapped |

---

## Feature 6: SEBI Risk Profiling

| AC ID | Acceptance Criterion | Test(s) | Status |
|-------|----------------------|---------|--------|
| AC6.1 | 18 questions covering all SEBI dimensions | `tests/integration/test_risk_profiler.py` | Mapped |
| AC6.2 | 5 risk categories produced | `tests/integration/test_risk_profiler.py` | Mapped |
| AC6.3 | 5-year retention stored | `tests/integration/test_risk_profiler.py` | Mapped |
| AC6.4 | Compliance pack has all Q&A | `tests/integration/test_pdf_generation.py::test_compliance_pack_contains_qa` | Mapped |
| AC6.5 | Empty rationale blocked at API | `tests/integration/test_risk_profiler.py` | Mapped |
| AC6.6 | Riskometer renders correct category | `frontend/src/tests/RiskProfiler.test.tsx` | Mapped |

---

## Should-Have Features

| SH ID | Feature | Test(s) | Status |
|-------|---------|---------|--------|
| SH1 | SIP Modeler client-side | `frontend/src/tests/SIPModeler.test.tsx` | Mapped |
| SH2 | Portfolio stress test | `frontend/src/tests/StressTest.test.tsx` | Mapped |
| SH3 | Retirement withdrawal simulator | `frontend/src/tests/RetirementWithdrawal.test.tsx` | Mapped |
| SH4 | SEBI disclaimer auto-injection | `tests/integration/test_pdf_generation.py::test_sebi_disclaimer_in_client_report` | Mapped |
| SH5 | Data freshness stale flag | `tests/integration/test_error_handling.py` | Mapped |

---

## Cross-Cutting Concerns

| CC ID | Concern | Test(s) | Status |
|-------|---------|---------|--------|
| CC1 | Cross-advisor isolation | `tests/security/test_advisor_isolation.py` | Mapped |
| CC2 | JWT auth on all endpoints | `tests/integration/test_auth.py` | Mapped |
| CC3 | API performance < 200ms | `tests/performance/test_api_latency.py` | Mapped |
| CC4 | PDF generation < 10 seconds | `tests/performance/test_api_latency.py` | Mapped |
| CC5 | Health endpoint responsive | `tests/integration/test_error_handling.py` | Mapped |

---

## Notes

### AC3.1 — FD Post-Tax Rate Detail

The test asserts the mathematically exact post-tax CAGR (not the naive approximation). At 7% pre-tax CAGR with 30% slab rate over 3 years the engine computes ~4.997% (slab rate on compounded gain), which is slightly above the naive 4.9% (slab rate on the pre-tax rate). Both figures confirm the tax is correctly applied. Test: `test_fd_30pct_bracket_accuracy`.

### Real-Data Tests (CI-Skipped)

Three tests in `tests/data_quality/test_return_accuracy.py` are decorated with `@pytest.mark.skipif(True, ...)` and are excluded from CI runs:

- `test_sbi_bluechip_3y_cagr_accuracy` — requires seeded AMFI NAV data
- `test_nifty50_index_1y_cagr_accuracy` — requires seeded NSE index history
- `test_ppf_historical_rate_accuracy` — requires RBI gazette data in DB

These must be executed manually after running the data ingestion pipeline (`scripts/ingest_amfi.py`).

### Frontend Tests

Frontend test paths listed above (e.g. `frontend/src/tests/AssetTable.test.tsx`) are located in the `frontend/` sibling directory of this backend repo and run via `npm test` in that package.
