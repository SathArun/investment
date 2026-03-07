---
title: "Phase 3: Analytics Engine"
status: completed
version: "1.0"
phase: 3
---

# Phase 3: Analytics Engine

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Application Data Models; TaxRule, AdvisorScoreComponents]` — Core computation models
- `[ref: SDD/Implementation Examples; Tax-Adjusted Return Computation]` — SGB vs Gold ETF walkthrough
- `[ref: SDD/Implementation Examples; Composite Score Normalization]` — Percentile normalization pattern
- `[ref: SDD/Complex Logic; compute_metrics algorithm]` — Nightly computation pseudocode
- `[ref: SDD/Implementation Gotchas]` — All four gotchas apply here

**Key Decisions**:
- ADR-6: Tax rules loaded from `data/reference/tax_rules.json`; not hardcoded
- Risk-free rate sourced from `config.py` (default 6.8% = 10Y G-sec yield); manually updated when RBI changes rates

**Dependencies**:
- Phase 1 complete (DB schema, tax_rules seeded)
- Phase 2 complete (`nav_history` and `index_history` populated with real data)

---

## Tasks

Builds the pure-Python analytics core: CAGR/risk metric computation, India-specific tax engine, and the nightly batch job that populates `computed_metrics`.

- [x] **T3.1 Returns calculator** `[activity: backend-analytics]`

  1. Prime: Read `[ref: SDD/Application Data Models; AdvisorScoreComponents]` and `[ref: SDD/Complex Logic; compute_metrics; steps 1-3]`
  2. Test: Given a pandas Series of 5 years of daily NAV (generated synthetically at 12% CAGR), assert: `compute_cagr(series, years=5)` returns value between 0.11 and 0.13; `compute_cagr` returns None if fewer than `years × 252` data points; `compute_rolling_returns(series, window_years=1)` returns a Series with length ≈ `len(series) - 252`; `compute_cagr` for a government-rate product (PPF, constant NAV) returns the configured rate exactly
  3. Implement: Create `app/analytics/returns.py` with `compute_cagr(nav_series, years)`, `compute_rolling_returns(nav_series, window_years)`, `get_nav_series(product_id, product_type, session)` (fetches from `nav_history` or `index_history`), `annualize_return(period_return, years)`
  4. Validate: Unit tests cover: 1Y/3Y/5Y/10Y CAGR with known synthetic series; None return for insufficient history; PPF/FD (flat rate series) CAGR equals stated rate; rolling return series length
  5. Success:
    - [ ] CAGR computation is accurate to ±0.5% vs manually verified calculation `[ref: PRD/Feature 1 AC; returns shown]`
    - [ ] Returns `None` (not an error) when history is shorter than requested period `[ref: SDD/Data Storage Schema; computed_metrics cagr_1y nullable]`

- [x] **T3.2 Risk metrics calculator** `[activity: backend-analytics]`

  1. Prime: Read `[ref: SDD/Application Data Models; AdvisorScoreComponents fields: std_dev, sharpe, sortino, max_drawdown]` and `[ref: SDD/Implementation Examples; Score Normalization; compute_sharpe_ratio]`
  2. Test: Given a synthetic NAV series with known properties (std_dev = 0.18 annualized, max drawdown = -0.38 at a specific date), assert: `compute_std_dev(series)` returns value within ±0.01 of 0.18; `compute_sharpe(series, risk_free=0.068)` is positive for a 12% CAGR series; `compute_sortino(series, risk_free=0.068)` ≥ Sharpe (fewer bad returns → higher Sortino); `compute_max_drawdown(series)` returns -0.38 ±0.01; PPF series (constant) returns std_dev=0, Sharpe=None (not zero/negative)
  3. Implement: Create `app/analytics/risk_metrics.py` with `compute_std_dev(nav_series)` (annualized from daily returns), `compute_sharpe(nav_series, risk_free_rate)`, `compute_sortino(nav_series, risk_free_rate)` (downside deviation only), `compute_max_drawdown(nav_series)` (rolling peak to trough); handle zero-variance series (PPF, G-Secs) by returning None for ratio metrics
  4. Validate: Unit tests covering: Nifty 50 historical data produces Sharpe ≈ 0.5–1.0; gold series produces lower Sharpe than equity in bull markets; FD series returns None for Sharpe; max drawdown for COVID 2020 period ≈ -0.38
  5. Success:
    - [ ] Sortino ≥ Sharpe for all series with low downside volatility `[ref: PRD/Feature 2 AC; risk-adjusted sub-scores]`
    - [ ] Zero-variance products (PPF, FDs) return None for Sharpe/Sortino — not NaN or 0 — so they receive special handling in the score engine `[ref: SDD/Implementation Examples; Score Normalization]`

- [x] **T3.3 Tax engine** `[activity: backend-analytics]`

  1. Prime: Read `[ref: SDD/Application Data Models; TaxRule]`, `[ref: SDD/Implementation Examples; SGB vs Gold ETF walkthrough]`, and `[ref: SDD/Implementation Gotchas; Annual LTCG exemption, Debt MF taxation]`
  2. Test: Write unit tests for ALL of the following scenarios (these are critical correctness tests):
     - FD at 30% bracket, 3Y hold → post-tax CAGR ≈ pre-tax × 0.70
     - PPF, any bracket → post-tax CAGR = pre-tax CAGR (EEE)
     - Equity MF LTCG (>12M), 12% pre-tax, 30% bracket, Rs 1L investment → LTCG rate 12.5%, Rs 1.25L exemption applied → post-tax ≈ 11.1%
     - Equity MF STCG (<12M), any return, 30% bracket → 20% tax regardless
     - Debt MF, 3Y hold, 30% bracket → slab rate 30% (NOT 12.5% LTCG) `[ref: SDD/Implementation Gotchas; Debt MF]`
     - Gold ETF, >12M, 12% CAGR, any bracket → 12.5% LTCG (no exemption threshold)
     - SGB, 8Y hold, 12% CAGR → post-tax = gross CAGR + 2.5% interest, 0% tax
     - SGB, 5Y hold (early exit secondary market) → 12.5% LTCG on gains
  3. Implement: Create `app/analytics/tax_engine.py` with `load_tax_rules()` (reads `data/reference/tax_rules.json`, filters by `effective_from ≤ today ≤ effective_until`), `find_applicable_rule(asset_class_id, holding_years)`, `compute_post_tax_cagr(asset_class_id, pre_tax_cagr, investment_inr, tax_bracket, holding_years)` per SDD pseudocode
  4. Validate: All 8 unit test scenarios pass. Run `compute_post_tax_cagr('bank_fd', 0.07, 100000, 0.30, 3)` → result ≈ 0.049; run `compute_post_tax_cagr('sgb', 0.12, 100000, 0.30, 8)` → result ≈ 0.148
  5. Success:
    - [ ] All 8 canonical tax scenarios return correct post-tax returns `[ref: PRD/Feature 3 Tax Overlay AC]`
    - [ ] Tax rules loaded from JSON, not hardcoded; changing `tax_rules.json` changes computation without code deploy `[ref: SDD/ADR-6]`
    - [ ] `effective_from`/`effective_until` filtering ensures correct rules applied for any historical period `[ref: SDD/ADR-6]`

- [x] **T3.4 Nightly metrics computation job** `[activity: backend-analytics]`

  1. Prime: Read `[ref: SDD/Complex Logic; compute_metrics algorithm]` (full pseudocode), `[ref: SDD/Data Storage Schema; computed_metrics table]`, `[ref: SDD/Quality Requirements; Performance: nightly job < 5 minutes]`
  2. Test: Given 5 schemes in `nav_history` with 3 years of synthetic data, assert: after running `compute_metrics`, the `computed_metrics` table has 5 rows with today's `computed_date`; each row has non-None `cagr_3y`, `std_dev_3y`, `sharpe_3y`; a scheme with < 3Y history has `cagr_5y = None`; running twice on the same day upserts (not duplicates) rows; a product with zero variance (PPF) has `sharpe_3y = None` and `std_dev_3y = 0`
  3. Implement: Create `app/jobs/compute_metrics.py` with `compute_all_product_metrics(session)` iterating over all active `asset_classes` + `mutual_funds`; use `returns.py` and `risk_metrics.py` functions; upsert into `computed_metrics` with `INSERT OR REPLACE`; log progress every 100 products
  4. Validate: Run on real data (top 50 funds from Phase 2); assert completion in < 60 seconds for 50 funds; check a known fund's 3Y CAGR against AMFI/mfapi.in published figure (±0.5% tolerance); assert no unhandled exceptions for funds with sparse data
  5. Success:
    - [ ] `computed_metrics` populated for all active products after job run `[ref: SDD/Complex Logic; compute_metrics]`
    - [ ] Job completes within 5 minutes for full ~2020 product universe `[ref: SDD/Quality Requirements; Performance]`
    - [ ] Sparse-history products produce None for metrics requiring unavailable history `[ref: SDD/Data Storage Schema; computed_metrics nullable columns]`

- [x] **T3.5 Phase 3 Validation** `[activity: validate]`

  - Run `pytest tests/unit/test_returns.py tests/unit/test_risk_metrics.py tests/unit/test_tax_engine.py`. All 8 tax scenarios must pass. Run `python -m app.jobs.compute_metrics` on real data and assert `computed_metrics` has rows. Run the SGB vs Gold ETF walkthrough from SDD manually and confirm expected output.

---

**Phase 3 Exit Criteria**: All analytics functions unit-tested; all 8 tax scenarios correct; `computed_metrics` table populated for all ingested products; nightly job runs in < 5 min.
