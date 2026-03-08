# India Investment Analyzer

A web application for SEBI-registered financial advisors to analyze, rank, and present Indian investment products across all asset classes. Advisors can assess client risk profiles, plan goals with SIP projections, run scenario analyses, and generate branded PDF reports.

---

## Architecture

**Modular Monolith** — single deployable unit with a clear internal module boundary.

| Layer | Technology |
|---|---|
| Backend API | FastAPI 0.115 (Python 3.11+) |
| ORM / Migrations | SQLAlchemy 2.0 + Alembic |
| Database | SQLite (Phase 1) |
| Background Jobs | APScheduler 3.10 |
| Analytics | pandas, numpy, scipy |
| PDF Generation | ReportLab + matplotlib |
| Frontend | React 18 + TypeScript (Vite 6) |
| State Management | Zustand 5 |
| Charts | Recharts 2 |
| Styling | Tailwind CSS 3 + Radix UI |
| Auth | JWT (python-jose) + bcrypt (passlib) |

---

## Repository Layout

```
investment/
├── CONSTITUTION.md          # Project coding rules and security contracts
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point, CORS, lifespan
│   │   ├── config.py        # Pydantic-settings configuration
│   │   ├── auth/            # JWT authentication + refresh token rotation
│   │   ├── clients/         # Client CRUD (advisor-scoped)
│   │   ├── goals/           # Investment goal CRUD
│   │   ├── market_data/     # Asset class + mutual fund catalogue + NAV history
│   │   ├── risk_profiler/   # 18-question SEBI risk questionnaire
│   │   ├── scenarios/       # Stress-test scenario data
│   │   ├── pdf/             # Branded PDF report generation
│   │   ├── analytics/       # Risk metrics, scoring engine, tax engine
│   │   ├── jobs/            # Scheduled data ingestion + compute jobs
│   │   └── db/              # SQLAlchemy base, session factory, seed data
│   ├── alembic/             # Database migrations
│   ├── data/reference/      # Static JSON: tax rules, stress scenarios, PPF rates, FD rates
│   ├── tests/               # Unit, integration, e2e, security, performance tests
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx           # Router and page layout
    │   ├── api/client.ts     # Axios instance with JWT interceptors
    │   ├── components/       # UI components (Dashboard, GoalPlanner, RiskProfiler, ScenarioPlanner, Presentation)
    │   ├── store/            # Zustand stores (auth, dashboard, filter, goal, risk profiler, UI)
    │   ├── utils/            # Finance math (SIP, retirement), risk labels
    │   └── types/            # TypeScript product types
    ├── package.json
    └── vite.config.ts
```

---

## Features

### Dashboard
- **Asset Table** — sortable list of investment products with risk/return metrics
- **Filter Bar** — filter by tax bracket, time horizon, asset category
- **Risk-Return Plot** — scatter chart of annualised return vs. standard deviation
- **Score Breakdown** — weighted composite scores per product
- **Client View Toggle** — simplified presentation mode for client-facing display
- **Product Pins** — advisor pins shortlisted products for the client view

### Goal Planner
- Create goals per client (target amount, target date, current corpus, monthly SIP)
- SIP projection with annual step-up and configurable expected return
- Inflation-adjusted target computation

### Risk Profiler
- 18-question SEBI-compliant questionnaire across 7 categories:
  Age, Income, Assets, Investment Objective, Investment Horizon, Behavioral Risk, Liquidity
- Scored 18–90; maps to five risk categories: **Conservative → Aggressive**
- Stores profile against the client record

### Scenario Planner
- **SIP Modeler** — projects future corpus for given SIP, step-up, return rate, and horizon
- **Stress Test** — applies historical stress scenarios (market crashes, rate shocks) to a portfolio value
- **Retirement Withdrawal** — simulates corpus drawdown over retirement with inflation

### PDF Reports
- Branded with advisor's firm name, logo, primary colour, and contact details
- Includes product tables, risk-return charts, and mandatory SEBI disclaimer
- Served as a downloadable file via the `/api/pdf/` endpoints

### Market Data Ingestion (Background Jobs)
| Job | Schedule | Source |
|---|---|---|
| AMFI daily NAV | 23:30 IST daily | AMFI API |
| Equity index prices | 16:30 IST weekdays | yfinance |
| NPS returns | 07:00 IST Mondays | NSDL / scraped |
| mfapi historical backfill | 02:00 IST Sundays | mfapi.in |
| Compute risk metrics | 01:00 IST nightly | Internal |
| Compute advisor scores | 00:00 IST nightly | Internal |

---

## Data Models

### `advisors`
| Column | Type | Notes |
|---|---|---|
| id | String PK | UUID |
| email | String UNIQUE | Login identity |
| password_hash | String | bcrypt |
| name, firm_name | String | Branding |
| logo_path, primary_color | String | PDF branding |
| sebi_registration | String | SEBI reg number |
| is_active | Boolean | Soft-disable |

### `clients`
| Column | Type | Notes |
|---|---|---|
| id | String PK | UUID |
| advisor_id | FK → advisors | Data isolation |
| name | String | |
| age | Integer | |
| tax_bracket | Float | 0 / 0.05 / 0.10 / 0.20 / 0.30 |
| risk_category | String | Conservative … Aggressive |

### `goals`
Linked to both `client` and `advisor`. Stores target amount, target date, current corpus, monthly SIP, annual step-up percentage, inflation rate, and expected return rate.

### `asset_classes`
Master catalogue of investment products with SEBI risk level (1–7), lock-in days, expense ratio, minimum investment, and data source.

### `mutual_funds`
Linked to `asset_classes`. Stores AMFI scheme code, name, AMC, direct/regular flag, expense ratio, AUM, fund manager.

### `nav_history` / `index_history`
Time-series price data keyed by (scheme_code or ticker, date).

---

## Scoring Engine

Each product is scored 0–100 on six dimensions, then combined into a single weighted composite:

| Dimension | Weight | Description |
|---|---|---|
| Risk-Adjusted (Sharpe) | 30% | Percentile rank of Sharpe ratio in universe |
| Tax-Adjusted Yield | 25% | Post-tax return considering STCG/LTCG rules |
| Liquidity | 15% | Based on lock-in days via lookup table |
| Expense Ratio | 10% | Lower expense = higher score |
| Return Consistency | 10% | Rolling-period return stability |
| Goal Fit | 10% | SEBI risk level vs. client time horizon alignment matrix |

---

## Analytics

- **`compute_std_dev`** — annualised daily-return standard deviation (252 trading days)
- **`compute_sharpe`** — annualised Sharpe ratio (risk-free rate: 6.8% 10Y G-sec default)
- **`compute_sortino`** — Sharpe variant using downside deviation only
- **`compute_max_drawdown`** — peak-to-trough maximum drawdown
- **Tax Engine** — date-effective STCG/LTCG rules loaded from `data/reference/tax_rules.json`; supports glob-pattern matching on asset class IDs

---

## API Endpoints

| Prefix | Module | Auth |
|---|---|---|
| `POST /api/auth/login` | auth | Public |
| `POST /api/auth/refresh` | auth | Public (refresh token) |
| `GET /api/market-data/products` | market_data | JWT |
| `GET /api/clients` | clients | JWT |
| `POST /api/clients` | clients | JWT |
| `GET/PUT /api/clients/{id}` | clients | JWT |
| `GET/POST /api/goals` | goals | JWT |
| `GET /api/risk-profiler/questions` | risk_profiler | JWT |
| `POST /api/risk-profiler/score` | risk_profiler | JWT |
| `GET /api/scenarios/stress-test` | scenarios | JWT |
| `POST /api/pdf/generate` | pdf | JWT |
| `GET /health` | root | Public |

All protected routes require `Authorization: Bearer <JWT>`. Cross-advisor access returns **404** (not 403) to prevent information disclosure.

---

## Frontend State Management

| Store | Responsibility |
|---|---|
| `authStore` | JWT tokens, advisor info, login/logout |
| `dashboardStore` | Product list, loading state, `fetchProducts` |
| `filterStore` | Tax bracket, time horizon, category filter |
| `goalStore` | Goal form state and API calls |
| `riskProfilerStore` | Questionnaire answers and computed score |
| `uiStore` | Client view toggle, selected product |

The Axios client in `api/client.ts` attaches the JWT on every request and transparently retries with a refreshed token on HTTP 401 before redirecting to `/login`.

---

## Security Model (from CONSTITUTION.md)

| Rule | Enforcement |
|---|---|
| **S1** JWT on all protected routes | `get_current_advisor` FastAPI dependency |
| **S2** Advisor data isolation | `WHERE advisor_id = current_advisor_id` in every service query |
| **S3** bcrypt password hashing | `passlib[bcrypt]`; only `password_hash` stored |
| **S4** Secrets from env vars | `pydantic-settings`; app fails to start without `JWT_SECRET_KEY` |
| **S5** No PII in logs or filenames | `structlog` used throughout |

---

## Getting Started

### Backend

```bash
cd backend
cp .env.example .env          # Set JWT_SECRET_KEY at minimum
pip install -r requirements.txt
alembic upgrade head          # Run migrations
python -m app.db.seed         # Seed reference data
uvicorn app.main:app --reload
```

Default DB: `sqlite:///./data/investment_analyzer.db`

### Frontend

```bash
cd frontend
npm install
npm run dev                   # Dev server on http://localhost:5173
```

The Vite dev server proxies `/api/*` to the backend.

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `JWT_SECRET_KEY` | Yes | — | HS256 signing key |
| `DATABASE_URL` | No | `sqlite:///./data/investment_analyzer.db` | SQLAlchemy URL |
| `JWT_ACCESS_EXPIRE_MINUTES` | No | 480 | Access token TTL |
| `JWT_REFRESH_EXPIRE_DAYS` | No | 30 | Refresh token TTL |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | Allowed origins |
| `ANGEL_ONE_API_KEY` | No | — | Optional Angel One data feed |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

## Testing

```bash
# Backend
cd backend
pytest                        # All tests
pytest tests/unit/            # Unit tests only
pytest tests/integration/     # Integration tests (requires running DB)

# Frontend
cd frontend
npm test                      # Vitest
```

Test coverage spans: unit (analytics, tax engine, ingestion jobs, scheduler), integration (auth, clients, market data API, PDF generation), security (advisor isolation), performance (API latency), e2e (advisor workflow), and data quality (return accuracy).

---

## Reference Data (`backend/data/reference/`)

| File | Contents |
|---|---|
| `asset_classes.json` | Master catalogue of investment categories |
| `tax_rules.json` | Date-effective STCG/LTCG rules per asset class pattern |
| `stress_scenarios.json` | Historical stress scenarios (shocks, drawdowns) |
| `ppf_rates.json` | Historical PPF interest rates |
| `fd_rate_ranges.json` | FD rate ranges by tenor |
| `index_tickers.json` | NSE/BSE index tickers for yfinance ingestion |
