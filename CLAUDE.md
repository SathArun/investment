# CLAUDE.md — India Investment Analyzer

A SEBI-compliant investment analysis platform for registered financial advisors. FastAPI backend + React/TypeScript frontend with nightly data ingestion, risk profiling, and branded PDF report generation.

---

## Architecture

**Modular monolith** — one deployable unit with clear internal module boundaries.

```
investment/
├── backend/           # FastAPI (Python 3.11+)
│   ├── app/
│   │   ├── main.py          # App entry point, CORS, lifespan
│   │   ├── config.py        # Pydantic-settings, env validation
│   │   ├── auth/            # JWT + refresh token rotation
│   │   ├── clients/         # Client CRUD (advisor-scoped)
│   │   ├── goals/           # Investment goal CRUD
│   │   ├── market_data/     # Product catalog + pre-computed scores
│   │   ├── risk_profiler/   # 18-question SEBI questionnaire
│   │   ├── scenarios/       # Stress test data
│   │   ├── pdf/             # ReportLab branded PDF generation
│   │   ├── analytics/       # Returns, risk metrics, score engine, tax
│   │   ├── jobs/            # APScheduler background jobs (no HTTP routes)
│   │   └── db/              # SQLAlchemy engine, session, seed
│   ├── alembic/             # Database migrations
│   ├── data/reference/      # Static JSON (tax rules, scenarios, rates)
│   └── tests/               # pytest (unit/integration/security/e2e)
└── frontend/          # React 18 + TypeScript (Vite 6)
    └── src/
        ├── api/             # Axios instance with JWT interceptor
        ├── components/      # Dashboard, GoalPlanner, RiskProfiler, PDF
        ├── store/           # Zustand stores (auth, dashboard, filters, goals, ui)
        ├── utils/           # Finance, retirement, riskLabel helpers
        └── tests/           # Vitest component tests
```

---

## Development Setup

### Backend

```bash
cd backend
cp .env.example .env          # Add JWT_SECRET_KEY (required)
pip install -r requirements.txt
alembic upgrade head           # Run DB migrations
python -m app.db.seed          # Seed reference data
uvicorn app.main:app --reload  # API on http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # Dev server on http://localhost:5173 (proxies /api → :8000)
```

---

## Common Commands

### Backend Tests

```bash
cd backend
pytest                            # All tests
pytest tests/unit/                # Unit tests
pytest tests/integration/         # Integration tests
pytest tests/security/            # Advisor data isolation
pytest tests/performance/         # API latency benchmarks
pytest tests/e2e/                 # Full advisor workflow
pytest -k "test_name"             # Single test
```

### Frontend

```bash
cd frontend
npm test          # Vitest (all component/integration tests)
npm run typecheck # TypeScript type check
npm run lint      # ESLint
npm run build     # Production build (tsc + vite build)
```

### Manual Job Execution

```bash
cd backend
python -m app.jobs.ingest_amfi       # Mutual fund NAVs (AMFI)
python -m app.jobs.ingest_equity     # NSE/BSE index prices (yfinance)
python -m app.jobs.ingest_nps        # NPS returns
python -m app.jobs.ingest_mfapi      # Historical NAV backfill
python -m app.jobs.compute_metrics   # CAGR, Sharpe, Sortino, max drawdown
python -m app.jobs.compute_scores    # 6-dimensional scores (~30k combinations)
```

### Database

```bash
cd backend
alembic upgrade head              # Apply all migrations
alembic revision --autogenerate -m "description"  # New migration
alembic downgrade -1              # Roll back one step
```

---

## Environment Variables

Set in `backend/.env` (copy from `.env.example`):

| Variable | Required | Default | Notes |
|---|---|---|---|
| `JWT_SECRET_KEY` | **Yes** | — | App refuses to start if missing |
| `DATABASE_URL` | No | `sqlite:///./data/investment_analyzer.db` | SQLAlchemy URL |
| `JWT_ACCESS_EXPIRE_MINUTES` | No | `480` | 8 hours |
| `JWT_REFRESH_EXPIRE_DAYS` | No | `30` | |
| `LOG_LEVEL` | No | `INFO` | |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | JSON list |
| `ANGEL_ONE_API_KEY` | No | — | Optional broker integration |

---

## Key APIs

All protected routes require `Authorization: Bearer <JWT>`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login` | Public | Returns access + refresh tokens |
| POST | `/api/auth/refresh` | Refresh token | Rotates tokens |
| GET | `/api/market-data/products` | JWT | Pre-computed scored products |
| GET/POST | `/api/clients` | JWT | List / create clients |
| GET/PUT | `/api/clients/{id}` | JWT | Get / update client |
| GET/POST | `/api/goals` | JWT | List / create goals |
| GET | `/api/risk-profiler/questions` | JWT | 18-question questionnaire |
| POST | `/api/risk-profiler/score` | JWT | Submit answers → risk score |
| GET | `/api/scenarios/stress-test` | JWT | Stress scenarios |
| POST | `/api/pdf/generate` | JWT | Generate branded PDF |
| GET | `/health` | Public | DB + scheduler status |

---

## Critical Security Rules

These are **non-negotiable** (from `CONSTITUTION.md`):

1. **All protected routes** must use the `get_current_advisor` FastAPI dependency.
2. **Advisor data isolation**: every DB query must include `WHERE advisor_id = current_advisor_id`. Cross-advisor access returns **404** (never 403 — avoid information disclosure).
3. **Passwords**: bcrypt via passlib. Only `password_hash` stored — never plaintext.
4. **Secrets from env only**: never hardcode. App fails to start if `JWT_SECRET_KEY` is missing.
5. **No PII in logs or filenames**: use `advisor_id` for scoping only.
6. **ORM only**: SQLAlchemy ORM for all DB access. No raw SQL strings (prevents injection).
7. **JWT in Authorization header only**: never cookies, never query params.
8. **Enum validation**: `tax_bracket` ∈ {0, 0.05, 0.10, 0.20, 0.30}; `risk_category` ∈ 5 SEBI types.
9. **Compliance records**: PDF/compliance packs are soft-delete only, retained 5 years, audit trail required.
10. **PDF filenames**: UUIDs only — no PII, no path traversal.
11. **External API calls** belong in `app/jobs/` only — never in FastAPI routes.

---

## Scoring Engine

Products are scored 0–100 on six dimensions and combined into a composite:

| Dimension | Weight | Source |
|---|---|---|
| Risk-Adjusted Return (Sharpe) | 30% | Percentile rank in universe |
| Tax-Adjusted Yield | 25% | Post-tax return (SEBI STCG/LTCG rules) |
| Liquidity | 15% | Lock-in days lookup |
| Expense Ratio | 10% | Lower = higher score |
| Return Consistency | 10% | Rolling-period stability |
| Goal Fit | 10% | SEBI risk level vs. client time horizon |

~30,300 combinations (product × tax_bracket × time_horizon) pre-computed nightly. Dashboard reads pre-computed scores only — never recomputes on request.

---

## Risk Profiler

18-question SEBI-compliant questionnaire mapping to **5 risk categories**:

| Score | Category |
|---|---|
| 18–35 | Conservative |
| 36–50 | Moderately Conservative |
| 51–63 | Moderate |
| 64–76 | Moderately Aggressive |
| 77–90 | Aggressive |

Compliance packs (questionnaire + score + SEBI disclaimer) must be retained 5 years — soft-delete only.

---

## Background Jobs (APScheduler)

Jobs run automatically in the background — all external data ingestion happens here.

| Job | Schedule (IST) |
|---|---|
| AMFI NAV ingestion | Daily 23:30 |
| Equity index ingestion | Weekdays 16:30 |
| NPS returns | Mondays 07:00 |
| mfapi historical backfill | Sundays 02:00 |
| Compute metrics | Daily 01:00 |
| Compute scores | Daily 00:00 |

External calls implement exponential backoff on 429/503. Failures retain the last successful data and never crash the scheduler or affect user-facing endpoints.

---

## Schema Changes

Always use Alembic migrations — never modify the DB schema directly:

```bash
cd backend
alembic revision --autogenerate -m "add column to clients"
alembic upgrade head
```

---

## Frontend State Management

Zustand stores (no Redux):

| Store | Purpose |
|---|---|
| `authStore` | JWT tokens, advisor info, login/logout |
| `dashboardStore` | Product list, loading, `fetchProducts` |
| `filterStore` | Tax bracket, time horizon, category filters |
| `goalStore` | Goal form state + API calls |
| `riskProfilerStore` | Questionnaire answers + computed score |
| `uiStore` | Client view toggle, selected product |

Vite dev server proxies `/api` to `localhost:8000` — no CORS issues in development.

---

## Reference Data

Static JSON files in `backend/data/reference/` (committed to repo, not from DB):

- `asset_classes.json` — investment product categories
- `tax_rules.json` — date-effective STCG/LTCG rules
- `stress_scenarios.json` — historical stress scenarios
- `ppf_rates.json` — PPF interest rate history
- `fd_rate_ranges.json` — FD rate ranges by tenor
- `index_tickers.json` — NSE/BSE tickers for yfinance

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Backend API | FastAPI 0.115.5, Python 3.11+ |
| Database | SQLite (SQLAlchemy 2.0 ORM + Alembic) |
| Background Jobs | APScheduler 3.10 |
| Analytics | pandas 2.2, numpy 2.1, scipy 1.14 |
| PDF Generation | ReportLab 4.2 + matplotlib 3.9 |
| Frontend | React 18, TypeScript, Vite 6 |
| State | Zustand 5 |
| UI Components | Radix UI + Tailwind CSS 3 |
| Charts | Recharts 2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Testing | pytest (backend), Vitest (frontend) |
