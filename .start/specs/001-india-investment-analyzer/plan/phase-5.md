---
title: "Phase 5: Auth, Clients, Goals & Risk Profiler API"
status: completed
version: "1.0"
phase: 5
---

# Phase 5: Auth, Clients, Goals & Risk Profiler API

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Internal API Changes; auth, clients, goals, risk profiler endpoints]`
- `[ref: SDD/Data Storage Schema; advisors, clients, goals, risk_profiles tables]`
- `[ref: SDD/System-Wide Patterns; Security]` — JWT, advisor_id scoping, bcrypt
- `[ref: PRD/Feature 5 Goal-Based Planner AC]` — Goal planner acceptance criteria
- `[ref: PRD/Feature 6 SEBI Risk Profiling AC]` — Risk profiling acceptance criteria
- `[ref: SDD/Implementation Gotchas; NPS age dependency]`

**Key Decisions**:
- All client data is scoped to `advisor_id` — no cross-advisor data leakage possible
- Risk profiling questionnaire: 15-20 questions; question bank in `app/risk_profiler/questionnaire.py`
- Goal planner: SIP step-up calculation and retirement corpus projection are server-side

**Dependencies**:
- Phase 1 complete (DB schema)
- Phase 4 complete (JWT dependency, `GET /api/products` used for goal product recommendations)

---

## Tasks

Implements user authentication, client management, goal-based financial planning, and SEBI-compliant risk profiling — the full advisor workflow backbone.

- [x] **T5.1 Authentication service** `[activity: backend-api]`

  1. Prime: Read `[ref: SDD/Internal API Changes; POST /api/auth/login, POST /api/auth/refresh]` and `[ref: SDD/System-Wide Patterns; Security; JWT]`
  2. Test: `POST /api/auth/login {email, password}` with valid credentials returns 200 with `access_token`, `refresh_token`, `advisor` object; invalid password returns 401; `POST /api/auth/refresh` with valid refresh token returns new access token; expired access token on a protected endpoint returns 401; `refresh_token` used twice returns 401 (rotation)
  3. Implement: Create `app/auth/service.py` with `create_advisor(email, password, name)` (bcrypt hash), `authenticate_advisor(email, password)`, `create_tokens(advisor_id)` (JWT access + refresh); `app/auth/router.py` with login and refresh endpoints; `app/auth/dependencies.py` with `get_current_advisor` FastAPI dependency (validates JWT on every request); seed one test advisor on `app/db/seed.py`
  4. Validate: Integration tests: valid login returns valid JWT; protected endpoint with no token → 401; protected endpoint with valid token → 200; token refresh works; second use of same refresh token → 401
  5. Success:
    - [ ] JWT access token expires in 8 hours `[ref: SDD/Deployment View; Configuration JWT_ACCESS_EXPIRE_MINUTES=480]`
    - [ ] All `/api/*` endpoints except `/api/auth/login` require valid JWT `[ref: SDD/System-Wide Patterns; Security]`
    - [ ] Passwords stored as bcrypt hash — plaintext never in DB `[ref: SDD/System-Wide Patterns; Security]`

- [x] **T5.2 Client management API** `[activity: backend-api]`

  1. Prime: Read `[ref: SDD/Internal API Changes; GET/POST/PATCH /api/clients]` and `[ref: SDD/Data Storage Schema; clients table]`
  2. Test: `POST /api/clients {name, age, tax_bracket, risk_category}` creates client scoped to authenticated advisor; `GET /api/clients` returns only that advisor's clients (not another advisor's); `PATCH /api/clients/{id}` updates client; attempting to access another advisor's client returns 404 (not 403 — no information disclosure)
  3. Implement: Create `app/clients/router.py` and `app/clients/service.py` with full CRUD, always filtering by `advisor_id` from JWT; validate `tax_bracket` in [0.0, 0.05, 0.10, 0.20, 0.30]; validate `risk_category` in the 5 valid categories
  4. Validate: Integration tests for all CRUD operations; cross-advisor access test; invalid tax_bracket returns 422; 20 clients inserted and returned correctly
  5. Success:
    - [ ] All client data strictly scoped to `advisor_id` from JWT `[ref: SDD/System-Wide Patterns; Security]`
    - [ ] `GET /api/clients` returns all clients for the advisor (used to populate client dropdown in UI) `[ref: PRD/User Journey; Pre-Meeting Preparation]`

- [x] **T5.3 Goal-based planner API** `[activity: backend-api]`

  1. Prime: Read `[ref: SDD/Internal API Changes; POST /api/goals, GET /api/goals/{id}/plan]` and `[ref: PRD/Feature 5 Goal-Based Planner AC]`
  2. Test: `POST /api/goals {client_id, name, target_amount_inr: 2500000, target_date: '2041-01-01', current_corpus_inr: 200000, monthly_sip_inr: 10000, annual_stepup_pct: 0.10, inflation_rate: 0.06}` creates goal; `GET /api/goals/{id}/plan` returns: `inflation_adjusted_target` > 2500000; `required_sip` > monthly_sip (gap exists); `recommended_allocation` contains items with `pct` summing to 100; for `annual_stepup_pct=0.0` corpus is lower than for `annual_stepup_pct=0.10`; 15-year goal with `tax_bracket=0.30` includes `nps_highlight: true`
  3. Implement: Create `app/goals/service.py` with `compute_goal_plan(goal, client)`: inflation-adjusted target = `target × (1 + inflation)^years`; gap = target - FV(current_corpus, return, years); `required_sip` via PMT formula with step-up; `goal_probability` from historical rolling returns distribution; `recommended_allocation` rules: 0-3Y → Liquid 40% + Corp Bond 40% + Gold 20%; 3-7Y → Balanced Hybrid 40% + Short Duration 30% + Gold 20% + REIT 10%; 7Y+ → Large Cap 50% + Mid Cap 20% + NPS 15% + Gold 10% + REIT 5%; NPS highlight if `years ≥ 10 AND tax_bracket ≥ 0.20`; `corpus_projection` at 3 return scenarios (conservative 8%, base 12%, optimistic 16%)
  4. Validate: Integration tests: 15-year retirement goal at Rs 2.5L investment returns corpus projection in reasonable range; SIP step-up at 10% produces ≥ 20% higher corpus vs 0% step-up; `required_sip` for gap = 0 (already on track) returns 0 or current SIP; NPS highlighted for 15Y goal at 30% bracket
  5. Success:
    - [ ] Inflation-adjusted target corpus shown `[ref: PRD/Feature 5 AC]`
    - [ ] NPS Tier 1 highlighted with 80CCD(1B) note for 15Y+ goals at 20%+ bracket `[ref: PRD/Feature 5 AC; NPS highlight]`
    - [ ] Annual Step-Up field updates projected corpus instantly (client-side calculation supported by this endpoint returning step-up-aware formula) `[ref: PRD/Feature 5 AC; step-up SIP]`

- [x] **T5.4 Risk profiler questionnaire + scoring** `[activity: backend-api]`

  1. Prime: Read `[ref: PRD/Feature 6 SEBI Risk Profiling AC]` — questionnaire captures age, income, assets, objectives, horizon, behavioral risk, liquidity; 5 risk categories output
  2. Test: `GET /api/risk-profiler/questions` returns ≥ 15 questions; each question has `id`, `text`, `category` (age/income/assets/objective/horizon/behavioral/liquidity), `options` with `value`, `label`, `score`; `POST /api/risk-profiles {client_id, responses, advisor_rationale}` with all conservative answers → `risk_category = 'Conservative'`; with all aggressive answers → `risk_category = 'Aggressive'`; missing required question response → 422; `advisor_rationale` empty string → 422 (rationale required for SEBI compliance)
  3. Implement: Create `app/risk_profiler/questionnaire.py` with 18 questions covering all SEBI-required dimensions; scoring: each answer scores 1-5, total normalized to 5 categories; `app/risk_profiler/service.py` with `compute_risk_score(responses)`, `assign_risk_category(score)`, `get_risk_description(category)` (plain-language description for client communication); store in `risk_profiles` with `retention_until = completed_at + 5 years`
  4. Validate: Unit tests for score computation: pure conservative responses → Conservative; mixed responses → Moderate; aggressive responses → Aggressive; boundary scores correctly assigned; integration test: full POST → correct DB row with `retention_until` set 5 years out
  5. Success:
    - [ ] Questionnaire captures all SEBI-required dimensions `[ref: PRD/Feature 6 AC]`
    - [ ] `retention_until` stored as `completed_at + 5 years` `[ref: PRD/Feature 6 AC; 5-year retention]`
    - [ ] 5 risk categories with written descriptions produced `[ref: PRD/Feature 6 AC; risk category output]`

- [x] **T5.5 Phase 5 Validation** `[activity: validate]`

  - Run `pytest tests/integration/test_auth.py tests/integration/test_clients.py tests/integration/test_goals.py tests/integration/test_risk_profiler.py`. Verify JWT auth works end-to-end. Test cross-advisor isolation. Test all 8 tax scenarios via `/api/tax/compute` endpoint. Verify goal plan NPS highlight logic.

---

**Phase 5 Exit Criteria**: Full auth works; client CRUD scoped by advisor; goal planner returns correct projections; risk profiler questionnaire complete with 5-category scoring; all integration tests pass.
