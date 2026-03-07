---
title: "Phase 1: Project Foundation & Database"
status: completed
version: "1.0"
phase: 1
---

# Phase 1: Project Foundation & Database

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Directory Map]` — Full project directory structure
- `[ref: SDD/Data Storage Schema]` — All 9 database tables
- `[ref: SDD/Project Commands]` — Setup and migration commands
- `[ref: SDD/Constraints CON-1, CON-2, CON-3]` — Tech stack and deployment constraints

**Key Decisions**:
- ADR-2: SQLite with SQLAlchemy ORM; Alembic migrations; PostgreSQL-compatible schema
- ADR-6: Reference data (tax rules, PPF rates, FD ranges) stored as JSON files in `data/reference/`

**Dependencies**:
- None — this is the foundation phase

---

## Tasks

Establishes the full project scaffold, database schema, and reference data seeding so all subsequent phases can build on a stable foundation.

- [ ] **T1.1 Backend project scaffold** `[activity: backend-infrastructure]`

  1. Prime: Read `[ref: SDD/Directory Map; backend/]` and `[ref: SDD/Project Commands]`
  2. Test: Verify `python -m uvicorn app.main:app` starts without errors; `pytest tests/` collects (0 tests is OK)
  3. Implement: Create `/backend` directory with `requirements.txt` (fastapi, uvicorn, sqlalchemy, alembic, pandas, numpy, scipy, yfinance, requests, python-jose, passlib, reportlab, matplotlib, apscheduler, structlog, pytest, httpx), `app/main.py` (FastAPI app init with CORS), `app/config.py` (Settings from env vars), `pytest.ini`, `.env.example`
  4. Validate: `pip install -r requirements.txt` succeeds; app starts; pytest runs without collection errors
  5. Success: FastAPI app responds to `GET /health → {"status": "ok"}` `[ref: SDD/Solution Strategy]`

- [ ] **T1.2 Database schema + migrations** `[activity: data-architecture]`

  1. Prime: Read `[ref: SDD/Data Storage Schema]` — all 9 tables with columns, types, constraints, and foreign keys
  2. Test: After running `python -m app.db.migrate`, assert all 9 tables exist: `advisors`, `clients`, `asset_classes`, `mutual_funds`, `nav_history`, `index_history`, `computed_metrics`, `advisor_scores`, `risk_profiles`, `goals`, `tax_rules`
  3. Implement: Create `app/db/base.py` (SQLAlchemy engine + session factory), ORM models in each module (`app/auth/models.py`, `app/market_data/models.py`, `app/analytics/models.py`, `app/goals/models.py`, `app/risk_profiler/models.py`), Alembic `env.py` + initial migration script, `app/db/migrate.py` runner
  4. Validate: `python -m app.db.migrate` creates `investment_analyzer.db`; `sqlite3 investment_analyzer.db .tables` shows all expected tables; foreign keys enforced; pytest unit test asserts schema via SQLAlchemy introspection
  5. Success:
    - [ ] All 9 tables created with correct columns and constraints `[ref: SDD/Data Storage Schema]`
    - [ ] `nav_history` primary key is `(scheme_code, nav_date)` composite `[ref: SDD/Data Storage Schema]`
    - [ ] `advisor_scores` primary key is `(product_id, product_type, tax_bracket, time_horizon, computed_date)` `[ref: SDD/Data Storage Schema]`

- [ ] **T1.3 Reference data files + seeding** `[activity: data-architecture]`

  1. Prime: Read `[ref: SDD/Data Storage Schema; tax_rules table]` and `[ref: SDD/Glossary; EEE, LTCG, STCG, SGB]`
  2. Test: After `python -m app.db.seed`, assert `tax_rules` table has rows covering: equity LTCG 12.5% (effective 2024-07-23), equity STCG 20% (effective 2024-07-23), debt MF slab rate (effective 2023-04-01), gold ETF LTCG 12.5%, SGB maturity tax-free, PPF EEE; assert `asset_classes` has ≥ 15 rows covering all asset class IDs from the SDD
  3. Implement: Create `data/reference/tax_rules.json` with all India tax rules per asset class pattern + effective dates; `data/reference/ppf_rates.json` (PPF rate history back to 2015); `data/reference/fd_rate_ranges.json` (major bank, small finance bank, post office rate bands); `data/reference/stress_scenarios.json` (COVID 2020, 2008 GFC, 2022 rate hike drawdown + recovery data); `data/reference/asset_classes.json` (all 15+ asset class definitions); `app/db/seed.py` that loads all JSON files into DB tables
  4. Validate: Unit tests assert each tax rule computes correctly for a known scenario (FD at 30% bracket → 4.9% post-tax on 7% pre-tax); stress scenario data has drawdown % and recovery months for each scenario
  5. Success:
    - [ ] `tax_rules` table populated with all India tax rules for FY2025-26 `[ref: PRD/Feature 3 Tax Overlay AC]`
    - [ ] Debt MF rule has `effective_from: 2023-04-01` and `tax_rate_expression: 'slab_rate'` `[ref: SDD/Implementation Gotchas; Debt MF taxation since April 2023]`
    - [ ] SGB rule has `special_rule: 'sgb_maturity_tax_free'` and `holding_period_months: 96` (8 years) `[ref: SDD/Implementation Examples; SGB vs Gold ETF]`

- [ ] **T1.4 Frontend project scaffold** `[activity: frontend-infrastructure]` `[parallel: true]`

  1. Prime: Read `[ref: SDD/Directory Map; frontend/]` and `[ref: SDD/Cross-Cutting Concepts; Design System]`
  2. Test: `npm run dev` starts Vite dev server; `npm run typecheck` passes; `npm run lint` passes on empty scaffold
  3. Implement: Create `/frontend` with `package.json` (react 18, typescript, vite, zustand, recharts, shadcn/ui, axios, tailwindcss), `vite.config.ts` (proxy `/api` → `http://localhost:8000`), Tailwind config, Shadcn/ui init, `src/main.tsx`, `src/App.tsx` (router shell), `src/api/client.ts` (axios instance with JWT interceptor), `tsconfig.json`
  4. Validate: `npm run dev` shows a blank page with no console errors; `npm run typecheck` clean; `npm run build` succeeds
  5. Success: Frontend scaffold runs at `localhost:5173` and proxies API calls to backend `[ref: SDD/Deployment View]`

- [ ] **T1.5 Phase 1 Validation** `[activity: validate]`

  - Run `pytest tests/unit/test_schema.py` (schema assertions). Run `python -m app.db.seed` and verify row counts. Run `npm run typecheck` and `npm run lint`. Confirm `GET /health` returns 200. Confirm all 9 tables exist in SQLite.

---

**Phase 1 Exit Criteria**: Backend starts, DB has all tables with correct schema, reference data is seeded, frontend scaffold runs, both projects lint-clean.
