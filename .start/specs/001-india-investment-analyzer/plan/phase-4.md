---
title: "Phase 4: Score Engine & Market Data API"
status: completed
version: "1.0"
phase: 4
---

# Phase 4: Score Engine & Market Data API

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Application Data Models; AdvisorScoreComponents]` — Score computation model + 6 sub-scores
- `[ref: SDD/Implementation Examples; Composite Score Normalization]` — Percentile normalization pattern
- `[ref: SDD/Internal API Changes; GET /api/products]` — Full ProductRow response schema
- `[ref: SDD/Data Storage Schema; advisor_scores table]` — Score persistence schema
- `[ref: PRD/Feature 2 Composite Advisor Score AC]` — Acceptance criteria for scoring

**Key Decisions**:
- ADR-3: Scores pre-computed nightly for all 5 tax brackets × 3 horizons; served from DB during day
- Liquidity and goal-fit sub-scores are asset-class-level constants (not recomputed from data)
- NPS liquidity score is age-dependent; `GET /api/products` accepts optional `client_age` param

**Dependencies**:
- Phase 1 complete (DB schema, asset_classes seeded)
- Phase 3 complete (`computed_metrics` table populated)

---

## Tasks

Builds the Composite Advisor Score computation engine and the core `GET /api/products` endpoint that powers the dashboard.

- [x] **T4.1 Composite score engine** `[activity: backend-analytics]`

  1. Prime: Read `[ref: SDD/Application Data Models; AdvisorScoreComponents]` and the score weights table in PRD `[ref: PRD/Detailed Feature Spec; Composite Advisor Score Engine]`
  2. Test: Given a mock `computed_metrics` row and a universe of 20 products with known Sharpe ratios, assert: `normalize_to_percentile(0.8, [0, 0.2, 0.3, 0.5, 0.8, 1.1])` returns ≈ 83.3; `compute_liquidity_score(0)` = 100; `compute_liquidity_score(-1)` = 10 (NPS); `compute_liquidity_score(5475)` = 20 (PPF); `compute_goal_fit(6, 'long')` = 100 (Very High risk, long horizon); `compute_goal_fit(1, 'short')` = 100 (Low risk, short horizon); `compute_goal_fit(6, 'short')` = 30; final composite score is weighted sum in range [0, 100]
  3. Implement: Create `app/analytics/score_engine.py` with `normalize_to_percentile(value, universe)` (scipy.stats.percentileofscore), `compute_liquidity_score(lock_in_days)` per SDD lookup table, `compute_goal_fit(sebi_risk_level, time_horizon)` per SDD alignment matrix, `compute_advisor_score(product_metrics, universe_metrics, tax_bracket, time_horizon)` returning all 6 sub-scores + composite; handle None Sharpe (0 percentile, not error)
  4. Validate: Unit tests: PPF scores high on consistency (100) and low on risk-adjusted (low percentile) and goal-fit for long horizon (40); Small-cap equity scores high on risk-adjusted and goal-fit(long) but low on consistency and liquidity (exit load); liquid fund scores 100 on liquidity; scores sum to correct weighted total
  5. Success:
    - [ ] Composite score is in range [0, 100] for all products `[ref: PRD/Feature 2 AC]`
    - [ ] Score Breakdown panel sub-scores sum to weighted composite (within floating point tolerance) `[ref: PRD/Feature 2 AC; score breakdown]`
    - [ ] PPF and G-Secs receive Consistency Score of 100 `[ref: PRD/Detailed Feature Spec; Business Rules]`
    - [ ] NPS Tier 1 receives Liquidity Score of 10 `[ref: PRD/Detailed Feature Spec; Business Rules]`

- [x] **T4.2 Nightly advisor score computation job** `[activity: backend-analytics]`

  1. Prime: Read `[ref: SDD/Complex Logic; compute_metrics; steps 5-8]` (score computation portion)
  2. Test: After running `compute_advisor_scores_job(session)` with 5 products in `computed_metrics`, assert: `advisor_scores` table has 5 × 5 × 3 = 75 rows (5 products × 5 brackets × 3 horizons); each row has `score_total` in [0, 100]; re-running the job on the same date upserts (does not duplicate); a product with all-None metrics receives a score of 50 (default median) with a data badge flag
  3. Implement: Create `app/jobs/compute_scores.py` with `compute_all_scores(session)`: iterate all bracket/horizon combinations, build universe vectors from `computed_metrics`, compute score for each product, upsert into `advisor_scores`; register this job in `scheduler.py` to run at 00:00 IST (after midnight, after AMFI job at 23:30)
  4. Validate: Run on real data (50 funds); assert 50 × 15 = 750 `advisor_scores` rows; assert Nifty 50 Index Fund ranks in top 3 for `long` horizon at `0.30` bracket; assert Liquid Fund ranks top 5 for `short` horizon
  5. Success:
    - [ ] All 30,300 score combinations computed in < 60 seconds `[ref: SDD/Complex Logic; PERFORMANCE NOTE]`
    - [ ] Scores re-rank correctly when bracket changes (lower tax bracket → SGB scores higher relative to FD) `[ref: PRD/Feature 2 AC; time horizon filter]`

- [x] **T4.3 Market Data API — GET /api/products** `[activity: backend-api]`

  1. Prime: Read `[ref: SDD/Internal API Changes; GET /api/products]` — full query params and ProductRow schema
  2. Test: Given 5 products in `advisor_scores` for bracket=0.30, horizon=long: `GET /api/products?tax_bracket=0.30&time_horizon=long` returns 200 with list of 5 ProductRows sorted by `advisor_score` desc; `GET /api/products?tax_bracket=0.30&time_horizon=long&sort_by=cagr_3y&sort_dir=asc` sorts by cagr_3y ascending; response includes `data_freshness` object with AMFI, equity, NPS timestamps; `GET /api/products?risk_filter=Conservative` filters to SEBI risk level ≤ 2; unauthenticated request returns 401
  3. Implement: Create `app/market_data/router.py` with `GET /api/products` endpoint; `app/market_data/service.py` with `get_products(session, tax_bracket, time_horizon, risk_filter, sort_by, sort_dir, client_age)` that queries `advisor_scores JOIN computed_metrics JOIN asset_classes`; serializes to `ProductRow` including score_breakdown; fetches `data_freshness` from a `job_runs` metadata table; applies NPS age-adjusted liquidity scoring if `client_age` provided
  4. Validate: Integration test: seed 10 products with known scores; `GET /api/products?tax_bracket=0.30&time_horizon=long` returns them sorted correctly; verify `post_tax_return_3y` matches expected tax calculation for FD (4.9% from 7% at 30%); verify SGB product shows higher post-tax than Gold ETF for long horizon; confirm response time < 200ms for 20 products
  5. Success:
    - [ ] Dashboard loads in < 3 seconds (API responds in < 200ms for 20 products) `[ref: SDD/Quality Requirements; Performance]`
    - [ ] Data freshness timestamps shown per data source category `[ref: PRD/Feature 1 AC; data refresh timestamps]`
    - [ ] Stale data (> 48h) flagged in response `[ref: SDD/Acceptance Criteria; WHEN data > 48h old]`

- [x] **T4.4 Product history endpoint — GET /api/products/{id}/history** `[activity: backend-api]`

  1. Prime: Read `[ref: SDD/Internal API Changes; GET /api/products/{product_id}/history]`
  2. Test: `GET /api/products/119551/history?period=5y` returns `returns_series` with ≥ 1000 data points; `rolling_1y` series length ≈ len(series) - 252; unknown product_id returns 404; period=1y returns fewer points than period=5y
  3. Implement: Add `/api/products/{product_id}/history` route in `app/market_data/router.py`; query `nav_history` or `index_history` by product_id and type; compute rolling returns on the fly (not pre-computed); return as list of `{date, value}` dicts
  4. Validate: Integration test with 5Y of synthetic NAV data; assert correct series lengths; verify rolling_1y aligns correctly to trailing-12-month windows
  5. Success: Historical chart data available for all products with ≥ 1Y history `[ref: PRD/Should Have Features; Rolling Return Comparison]`

- [x] **T4.5 Phase 4 Validation** `[activity: validate]`

  - Run `pytest tests/unit/test_score_engine.py tests/integration/test_market_data_api.py`. Assert `GET /api/products` returns 200 with correctly scored products. Verify SGB scores higher than Gold ETF at 30% bracket long horizon. Assert score sub-components sum correctly. Confirm response time < 200ms.

---

**Phase 4 Exit Criteria**: All 30,300 advisor scores computed; `GET /api/products` returns ranked, tax-adjusted, scored products in < 200ms; product history endpoint works; all unit and integration tests pass.
