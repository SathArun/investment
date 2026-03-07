# Project Constitution

> Version: 1.1.0 | Last Updated: 2026-03-06
> Project Type: Modular Monolith (single-app) — FastAPI (Python 3.11+) backend + React 18 (TypeScript) frontend

## Security

### S1 — JWT Required on All Protected Routes [L1]

```yaml
level: L1
check: All /api/* routes except /api/auth/login require valid JWT via get_current_advisor dependency
scope: "app/**/router.py"
message: Route missing JWT dependency. Add get_current_advisor to all protected endpoints.
```

All API endpoints except `/api/auth/login` must use the `get_current_advisor` FastAPI dependency to enforce JWT authentication.

### S2 — Advisor Data Isolation via advisor_id [L1]

```yaml
level: L1
check: All queries returning user data must filter by WHERE advisor_id = current_advisor_id
scope: "app/**/service.py"
message: Cross-advisor data leakage risk. Add advisor_id filter to this query. Cross-advisor access must return 404, not 403.
evidence: solution.md:1112, phase-5.md:51
depends_on: S1
```

All client/advisor data must be scoped to `advisor_id` from the JWT. **Requires S1** — `current_advisor_id` is populated by the `get_current_advisor` dependency (S1). Cross-advisor access returns `404` (not `403`) to prevent information disclosure.

### S3 — Bcrypt Password Hashing [L1]

```yaml
level: L1
pattern: "password\\s*[:=]\\s*['\"][^'\"]+['\"]"
scope: "app/**/*.py"
message: Plaintext password detected. Use bcrypt hashing via passlib.
evidence: solution.md:406, phase-5.md:46
```

Passwords must be hashed with bcrypt via `passlib`. The `advisors` table stores only `password_hash`. Plaintext passwords must never be stored.

### S4 — Secrets from Environment Variables [L1]

```yaml
level: L1
pattern: "(JWT_SECRET_KEY|api_key|secret|password|token)\\s*=\\s*['\"][^'\"]{8,}['\"]"
scope: "**/*.{py,ts,json,yaml,yml}"
exclude: "**/*.example, **/*.test.py, **/*.spec.ts"
message: Hardcoded secret detected. Use environment variables via app/config.py.
evidence: solution.md:1020, phase-9.md:91
```

All secrets loaded from environment variables. Application must fail to start with a clear error message if `JWT_SECRET_KEY` or other required secrets are missing.

### S5 — No PII in Logs or Filenames [L1]

```yaml
level: L1
check: Client names and email addresses must not appear in log fields or PDF filenames
scope: "app/**/*.py"
message: PII detected in log statement or filename. Use advisor_id for scoping only.
evidence: solution.md:1115
```

Structured logs include `advisor_id` for scoping but must never include client names, emails, or other personal data. PDF filenames must not contain client names.

### S6 — SQLAlchemy ORM Only (No Raw SQL) [L1]

```yaml
level: L1
pattern: "session\\.execute\\s*\\(\\s*['\"]\\s*(SELECT|INSERT|UPDATE|DELETE)"
scope: "app/**/*.py"
message: Raw SQL string detected. Use SQLAlchemy ORM methods instead.
evidence: solution.md:1129, phase-1.md:45
```

All database queries must use SQLAlchemy ORM. No raw SQL strings passed to `session.execute()`.

### S7 — JWT Delivery and Transport [L1]

```yaml
level: L1
check: POST /api/auth/login returns JWT in JSON response body ({access_token, refresh_token}). Tokens stored client-side in memory/localStorage. All subsequent requests pass JWT as Authorization: Bearer header only — never in URL query parameters.
scope: "frontend/src/**/*.{ts,tsx}, app/auth/router.py"
message: JWT must not appear in URL params. Login must return tokens in JSON body. Use Authorization header via the shared Axios instance.
evidence: phase-7.md:3, solution.md:131
```

### S8 — Enum Validation for Tax Bracket and Risk Category [L1]

```yaml
level: L1
check: tax_bracket must be in [0.0, 0.05, 0.10, 0.20, 0.30]; risk_category must be one of 5 SEBI categories. Invalid values return HTTP 422.
scope: "app/**/router.py, app/**/models.py"
message: Missing enum validation for tax_bracket or risk_category. Add Pydantic validator.
evidence: phase-5.md:52-53
```

### S9 — Compliance PDF Retention, Immutability, and Audit Trail [L1]

```yaml
level: L1
check: retention_until = completed_at + 5 years; PDFs stored in per-advisor directories; compliance packs use soft-delete only (never physically deleted); all modifications logged with advisor_id, timestamp, and change description
scope: "app/pdf/**/*.py, app/risk_profiler/**/*.py"
message: Missing retention_until, hard-delete detected, or missing audit log entry on compliance pack. SEBI audit trail required.
evidence: solution.md:507, solution.md:1170, phase-5.md:73, requirements.md:159
```

Compliance packs and risk profiles must never be physically deleted (`is_deleted` flag only). Any modification must write an audit log entry with `advisor_id`, `modified_at`, and `change_description`. Retention enforced for exactly 5 years from `completed_at`.

### S10 — HTTPS in Production [L2]

```yaml
level: L2
check: HTTPS (TLS 1.2+) required for all communication in production deployments. No HTTP allowed for any endpoint.
scope: "deployment"
message: Ensure HTTPS/TLS 1.2+ is configured before production deployment (CON-6).
evidence: solution.md:1112
```

### S11 — Encryption at Rest for Sensitive Data [L2]

```yaml
level: L2
check: SQLite database file and PDF storage directory must be on an encrypted volume or use application-level encryption for sensitive fields (client names, risk profiles, goals). Verified before production deployment.
scope: "deployment, app/db/**/*.py"
message: Sensitive client financial data must be encrypted at rest (CON-6). Ensure encrypted storage volume or field-level encryption.
evidence: solution.md:43
```

All client data (names, risk profiles, goals, financial details) is sensitive personal financial information. CON-6 explicitly requires encryption at rest and in transit.

### S12 — SEBI Riskometer Color Compliance [L1]

```yaml
level: L1
check: Risk category display uses exactly 5 SEBI-mandated categories (Conservative, Moderately Conservative, Moderate, Moderately Aggressive, Aggressive) with corresponding SEBI riskometer colors. No custom category names or colors.
scope: "frontend/src/components/**/*.tsx, frontend/src/**/*.{ts,tsx}"
message: Non-SEBI risk category or color detected. Use only the 5 official SEBI categories with mandated color palette.
evidence: requirements.md:162, solution.md:1063
```

### S13 — Secure PDF Filenames (UUID, No Path Traversal) [L1]

```yaml
level: L1
pattern: "\\.\\./|%2e%2e|path\\.join.*request|filename.*client_name|filename.*advisor_name"
scope: "app/pdf/**/*.py"
message: Path traversal risk or PII in PDF filename detected. Use UUID-based filenames only. Validate all storage paths against the per-advisor directory boundary.
evidence: solution.md:1170
```

PDF filenames must be UUID-based (`{uuid4()}.pdf`). Storage paths must be validated to prevent directory traversal. No client names, advisor names, or user-controlled strings in filenames.

---

## Architecture

### A1 — 4-Layer Modular Monolith [L1]

```yaml
level: L1
check: Single deployable unit with 4-layer separation: Data Ingestion -> Analytics -> REST API -> React SPA. No microservices.
scope: "project"
message: Architecture violation. All layers must remain in a single deployable unit (ADR-1).
evidence: solution.md:212-214, solution.md:1122-1126
```

Layer boundaries:
- **Data Ingestion**: `app/jobs/` — APScheduler background jobs only
- **Analytics Engine**: `app/analytics/` — financial calculations
- **REST API**: `app/*/router.py` + `app/*/service.py`
- **Frontend**: `frontend/src/`

### A2 — FastAPI Routes Must Not Call External APIs [L1]

```yaml
level: L1
check: No httpx/requests/yfinance calls inside router.py or service.py files
scope: "app/**/router.py, app/**/service.py"
message: External API call detected in route/service layer. Move to app/jobs/ scheduler job.
evidence: solution.md:215-216
```

All external data flows through scheduled APScheduler jobs that write to SQLite. The FastAPI layer reads from the database only — never calls external APIs during a user request.

### A3 — Feature Module Structure [L1]

```yaml
level: L1
check: Each feature module must have router.py, service.py, and models.py. No ORM calls in router.py.
scope: "app/**/"
message: Missing module file or ORM call in router. Routers delegate to service layer only.
evidence: solution.md:288-332, solution.md:1038-1040
```

Feature modules: `auth`, `market_data`, `goals`, `risk_profiler`, `pdf`. Each must follow the `router.py` / `service.py` / `models.py` triplet.

### A4 — Pre-Computed Scores Only; No On-Demand Computation [L1]

```yaml
level: L1
check: Dashboard API reads from advisor_scores table only. Score computation must not be triggered by user requests.
scope: "app/market_data/router.py, app/market_data/service.py"
message: On-demand score computation detected. Serve pre-computed advisor_scores rows only (ADR-3).
evidence: solution.md:1134-1138
```

All ~30,300 score combinations (product × tax_bracket × time_horizon) are pre-computed nightly by the `compute_metrics` APScheduler job. The database `SELECT` on `advisor_scores` must complete in < 1 second (query only). Total dashboard load including serialization and frontend render must be < 3 seconds (see P1).

### A5 — Tax Rules as JSON Data [L1]

```yaml
level: L1
pattern: "(0\\.125|0\\.20|0\\.30|12\\.5|LTCG|slab_rate)\\s*[=*]"
scope: "app/analytics/**/*.py"
message: Hardcoded tax percentage detected. Load tax rules from data/reference/tax_rules.json via load_tax_rules().
evidence: solution.md:1152-1156, ADR-6
```

Tax rules stored in `data/reference/tax_rules.json` with `effective_from`/`effective_until` date fields. All tax calculations use `load_tax_rules()`. Tax rule updates require JSON edits only — no code redeploy.

### A6 — ReportLab for PDF Generation [L1]

```yaml
level: L1
check: All PDF generation uses ReportLab. No WeasyPrint, Puppeteer, or headless Chrome.
scope: "app/pdf/**/*.py"
message: Non-ReportLab PDF dependency detected. Use ReportLab for deterministic, browser-free PDF generation (ADR-4).
evidence: solution.md:1140-1144
```

### A7 — Zustand for State Management (No Redux) [L1]

```yaml
level: L1
pattern: "from 'redux'|from '@reduxjs/toolkit'|createSlice|useDispatch|useSelector"
scope: "frontend/src/**/*.{ts,tsx}"
message: Redux detected. Use Zustand only (ADR-7). Store files: src/store/{feature}Store.ts
evidence: solution.md:1158-1162
```

### A8 — Advisor-Only Components Behind advisorMode Guard [L1]

```yaml
level: L1
check: Sub-scores, Sharpe/Sortino ratios, and numerical metrics rendered only inside {advisorMode && <Component />}
scope: "frontend/src/components/**/*.tsx"
message: Advisor-only metric rendered without advisorMode guard. Client View must not expose this data.
evidence: solution.md:1050-1052
```

### A9 — Single Axios Instance [L2]

```yaml
level: L2
check: All HTTP calls use the shared Axios instance from src/api/client.ts with JWT interceptor
scope: "frontend/src/**/*.{ts,tsx}"
message: Direct axios.create() or fetch() call detected. Use the shared src/api/client.ts instance.
evidence: phase-7.md:42-45
```

### A10 — Alembic Migration Required for Schema Changes [L2]

```yaml
level: L2
check: All schema changes accompanied by an Alembic migration script; schema stays PostgreSQL-compatible
scope: "app/db/**/*.py"
message: Schema change without migration detected. Run alembic revision --autogenerate (ADR-2).
evidence: solution.md:1128-1132
```

### A11 — Score Normalization Weights [L3]

```yaml
level: L3
check: Sub-score weights sum to 100%: Risk-Adj Return 30%, Tax-Adj Yield 25%, Liquidity 15%, Cost 10%, Consistency 10%, Goal-Fit 10%. Normalization universe = ALL products in the database at compute time.
scope: "app/analytics/score_engine.py, app/analytics/**/*.py"
message: Score weight mismatch or per-category normalization detected. Normalize against full product universe.
evidence: solution.md:200-232, solution.md:822-855
```

### A12 — External API Rate Limiting & Graceful Degradation [L1]

```yaml
level: L1
check: All external API calls in app/jobs/ implement retry with exponential backoff on 429/503 responses. On failure, retain last successful data and set data_freshness timestamp. Never propagate external API errors to user-facing requests.
scope: "app/jobs/**/*.py"
message: Missing backoff/retry logic for external API call. Implement exponential backoff and retain last-known-good data on failure.
evidence: solution.md:970, solution.md:965
```

Rate limit handling per source: mfapi.in 429 → backoff 60s + retry; AMFI API down → retain yesterday's NAV data; yfinance failure → retain last index prices. All job failures must update `data_freshness` table and never crash the scheduler.

---

## Code Quality

### Q1 — Naming Conventions [L1]

```yaml
level: L1
check: Python files/functions/variables snake_case; Python classes PascalCase; constants UPPER_SNAKE_CASE. React components PascalCase; hooks/stores/utils camelCase. DB tables/columns snake_case; FK columns {table}_id; booleans is_ prefix.
scope: "app/**/*.py, frontend/src/**/*.{ts,tsx}"
message: Naming convention violation. See constitution Q1 for rules.
evidence: solution.md:287-331, solution.md:403-533
```

### Q2 — TypeScript Strict Mode; No `any` [L1]

```yaml
level: L1
pattern: ":\\s*any\\b"
scope: "frontend/src/**/*.{ts,tsx}"
exclude: "**/*.test.tsx, **/*.spec.ts"
message: any type detected. Use explicit TypeScript types or generics.
evidence: phase-1.md:67, phase-7.md:66
```

`npm run typecheck` must pass with zero errors before any commit.

### Q3 — ESLint Must Pass [L1]

```yaml
level: L1
check: npm run lint passes with zero errors
scope: "frontend/src/**/*.{ts,tsx}"
message: ESLint errors detected. Fix before committing.
evidence: phase-1.md:66
```

### Q4 — Structured Logging via structlog [L1]

```yaml
level: L1
pattern: "print\\s*\\(|console\\.(log|debug|info)"
scope: "app/**/*.py, frontend/src/**/*.{ts,tsx}"
exclude: "**/*.test.py, **/*.test.tsx, **/*.spec.ts"
message: print()/console.log() in production code. Use structlog (backend) or remove (frontend).
evidence: solution.md:1115
```

Backend: use `structlog` with fields `timestamp`, `level`, `advisor_id`, `endpoint`, `duration_ms`, `error`. No `print()`.

### Q5 — Standardized API Error Format [L1]

```yaml
level: L1
check: All FastAPI exception handlers return {"error": "UPPER_SNAKE_CASE_CODE", "message": "...", "details": {...}}
scope: "app/**/*.py"
message: Non-standard error response shape. Use {error, message, details} format.
evidence: solution.md:1113
```

### Q6 — Axios 401 Auto-Refresh Interceptor [L1]

```yaml
level: L1
check: 401 response triggers token refresh via /api/auth/refresh then retries original request once before redirecting to login
scope: "frontend/src/api/client.ts"
message: 401 handling missing or incomplete in Axios interceptor.
evidence: solution.md:1113, phase-7.md:45
```

### Q7 — India Locale Formatting [L1]

```yaml
level: L1
check: Currency displayed as Rs/Lakh/Crore (not USD). Dates formatted as DD-Mon-YYYY.
scope: "frontend/src/**/*.{ts,tsx}"
message: Incorrect currency or date format. Use formatCurrency() and formatDate() from src/utils/.
evidence: solution.md:1116
```

### Q8 — Graceful Ingestion Error Handling [L2]

```yaml
level: L2
check: Data ingestion jobs catch row-level parse errors, log the failing row content, and continue processing. Jobs must not abort on individual row failures.
scope: "app/jobs/**/*.py"
message: Missing try/except around row processing. Log and continue; do not raise.
evidence: phase-2.md:37-42, phase-2.md:49
```

Log progress every 100 records processed.

### Q9 — Comments Explain Why, Not What [L2]

```yaml
level: L2
check: Complex financial algorithms preceded by pseudocode. Non-obvious tax rules (SGB maturity, Debt MF post-April 2023) explained inline.
scope: "app/analytics/**/*.py"
message: Missing explanation for complex logic. Add a comment describing why this calculation is done this way.
evidence: solution.md:809-810, solution.md:822-834
```

---

## Testing

### T1 — Test Framework Stack [L1]

```yaml
level: L1
check: Backend uses pytest; frontend uses Vitest + React Testing Library; E2E uses Playwright
scope: "tests/**/*.py, frontend/src/**/*.test.tsx"
message: Wrong test framework detected. Use pytest (backend), Vitest+RTL (frontend), Playwright (E2E).
evidence: phase-1.md:37, phase-7.md, phase-9.md
```

### T2 — Test Directory Structure [L1]

```yaml
level: L1
check: Backend tests in tests/unit/, tests/integration/, tests/security/, tests/data_quality/, tests/performance/, tests/e2e/. Frontend tests co-located as *.test.tsx.
scope: "tests/"
message: Test file in wrong directory. Place in the appropriate subdirectory by test type.
evidence: phase-2.md:87, phase-9.md
```

### T3 — All 8 Canonical Tax Scenarios Must Pass [L1]

```yaml
level: L1
check: tests/unit/test_tax_engine.py covers all 8 canonical tax scenarios with exact correctness (no tolerance)
scope: "app/analytics/tax_engine.py"
message: Canonical tax scenario test missing or failing. All 8 scenarios required for correctness.
evidence: phase-3.md:56-68
```

Examples: Equity LTCG below Rs 1.25L exemption, Debt MF post-April 2023 slab rate, SGB 8-year tax-free maturity, PPF EEE treatment.

### T4 — Cross-Advisor Isolation Test Required [L1]

```yaml
level: L1
check: tests/security/test_advisor_isolation.py verifies Advisor B cannot access Advisor A's data. Expect 404, not 403.
scope: "app/**/service.py"
message: Cross-advisor isolation test missing. Required for security validation.
evidence: phase-9.md:50
```

### T5 — Performance Assertions in Tests [L2]

```yaml
level: L2
check: API endpoint tests assert response < 200ms for 20 products; PDF generation test asserts < 10 seconds; nightly job test asserts < 5 minutes
scope: "tests/performance/**/*.py, tests/integration/**/*.py"
message: Missing performance assertion. Add timing check to this test.
evidence: phase-4.md:63, phase-6.md:52, phase-3.md:79
```

### T6 — CAGR Accuracy Within 0.5% of AMFI Published Figures [L2]

```yaml
level: L2
check: tests/data_quality/test_return_accuracy.py spot-checks at least 5 known funds against AMFI published 3Y CAGR. Tolerance: ±0.5%.
scope: "app/analytics/returns.py"
message: CAGR accuracy test missing or tolerance exceeded.
evidence: phase-9.md:T9.3
```

### T7 — PRD Acceptance Criteria Traceability [L3]

```yaml
level: L3
check: tests/traceability.md maps all 35+ PRD Gherkin acceptance criteria to passing test file + test name. Zero unmapped criteria at Phase 9 completion.
scope: "tests/"
message: Unmapped PRD acceptance criteria detected. Update tests/traceability.md.
evidence: phase-9.md:T9.7
```

---

## Dependencies

### D1 — Exact Version Pinning [L1]

```yaml
level: L1
check: All packages in requirements.txt and package.json use exact versions (no ranges, no ^ or ~)
scope: "requirements.txt, frontend/package.json"
message: Non-exact version detected. Pin to exact version for reproducibility.
evidence: phase-1.md:37
```

### D2 — Phase 1 Uses Free APIs Only [L1]

```yaml
level: L1
check: No paid vendor API integrations in Phase 1. Approved sources: AMFI, mfapi.in, yfinance, NPSTRUST, RBI/GOI published rates. All approved sources must be called ONLY from app/jobs/ (per A2) — never from router.py or service.py.
scope: "app/jobs/**/*.py"
message: Paid API integration detected, or approved source called outside app/jobs/. Defer paid APIs to Phase 2 (CON-2: infrastructure cost < Rs 2000/month).
evidence: solution.md:35
```

### D3 — Optional API Keys Must Not Block Startup [L2]

```yaml
level: L2
check: ANGEL_ONE_API_KEY and other optional paid API keys gracefully absent; application starts normally without them
scope: "app/config.py"
message: Optional API key causing startup failure. Mark as Optional in config with graceful fallback.
evidence: phase-9.md:91
```

### D4 — Backup and Disaster Recovery [L2]

```yaml
level: L2
check: SQLite database and PDF storage must have a documented daily backup process. Backup retention >= 30 days. Recovery procedure documented and tested quarterly. Backup includes: database file, data/reference/ JSON files, data/pdfs/ directory.
scope: "deployment"
message: No backup strategy documented or implemented. Client financial data and 5-year compliance packs require daily backups with off-site replication.
evidence: requirements.md:265-266, solution.md:1171
```

---

## Performance

### P1 — Dashboard Load Under 3 Seconds [L2]

```yaml
level: L2
check: Dashboard initial load (pre-computed scores + render) completes in < 3 seconds
scope: "app/market_data/router.py, frontend/src/components/Dashboard/"
message: Dashboard load performance target missed. Verify single-query advisor_scores read and Zustand caching.
evidence: solution.md:1168
```

### P2 — Filter Re-Sort Performance [L2]

```yaml
level: L2
check: Score re-sort on bracket/horizon filter change < 500ms (client-side Zustand). Tax bracket change < 1s (server-side).
scope: "frontend/src/store/filterStore.ts, frontend/src/store/dashboardStore.ts"
message: Filter re-sort exceeds target. Use optimistic client-side sort from Zustand cache; only hit server for tax bracket changes.
evidence: solution.md:1168
```

### P3 — PDF Generation Under 10 Seconds [L2]

```yaml
level: L2
check: PDF generation for max 5 products completes in < 10 seconds. Show error at 15-second timeout.
scope: "app/pdf/**/*.py"
message: PDF generation exceeds 10-second target. Max 5 products; optimize ReportLab layout.
evidence: solution.md:1168, phase-6.md:52
```

### P4 — Nightly Metrics Job Under 5 Minutes [L2]

```yaml
level: L2
check: compute_metrics job processes ~30,300 score rows in < 5 minutes using pandas/numpy vectorization
scope: "app/jobs/compute_metrics.py"
message: Nightly job exceeds 5-minute target. Replace Python loops with pandas/numpy vectorized operations.
evidence: solution.md:1168, solution.md:1002-1004
```

### P5 — Data Staleness Warning [L2]

```yaml
level: L2
check: Prominent staleness warning displayed when any data source is > 48 hours old
scope: "frontend/src/components/Dashboard/, app/market_data/service.py"
message: Missing staleness check. Show banner with source name and last-updated timestamp when data > 48h.
evidence: solution.md:1181
```

### P6 — Canvas Rendering for Large Time-Series [L3]

```yaml
level: L3
check: Time-series charts with > 1000 data points use Canvas rendering, not SVG
scope: "frontend/src/components/**/*.tsx"
message: SVG chart with large dataset detected. Switch to Canvas renderer for performance.
evidence: solution.md:1114
```

---

## Scheduler

### J1 — Scheduled Job Failure & Recovery [L2]

```yaml
level: L2
check: Each APScheduler job must catch all exceptions at the job level, log the failure with job name and error details, update the data_freshness table with failure status, and NOT crash the scheduler process. Jobs must be individually retrievable (e.g., scheduler.run_job('ingest_amfi')).
scope: "app/jobs/**/*.py"
message: Unhandled exception at job level detected. Wrap entire job in try/except, log failure, update data_freshness, and continue scheduler operation.
evidence: solution.md:965, solution.md:1002-1004
```

The APScheduler process must remain running even if individual jobs fail. Job failure must surface to the user via the staleness warning (P5) within 5 minutes. Critical path: `compute_metrics` job failure → dashboard serves stale scores → P5 staleness banner must appear.

---

## Custom Rules

<!-- Add project-specific rules here as the codebase evolves -->
