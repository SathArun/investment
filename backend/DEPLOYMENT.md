# India Investment Analyzer — Deployment Guide

## Prerequisites

- Python 3.11 or higher
- Node 18 or higher (for the frontend)
- Git

## Backend Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd investment
```

### 2. Create and activate a virtual environment

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set JWT_SECRET_KEY to a strong random value
```

### 5. Initialise the database

```bash
python -m app.db.seed
```

### 6. Ingest AMFI fund data (first run)

```bash
python -m app.jobs.ingest_amfi
```

### 7. Start the API server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API is now available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

---

## Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

The frontend is available at `http://localhost:5173`.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `JWT_SECRET_KEY` | Yes | — | Secret used to sign JWT tokens. Must be a long random string. |
| `DATABASE_URL` | No | `sqlite:///./data/investment_analyzer.db` | SQLAlchemy database URL. |
| `JWT_ACCESS_EXPIRE_MINUTES` | No | `480` | Access token TTL in minutes (8 hours). |
| `JWT_REFRESH_EXPIRE_DAYS` | No | `30` | Refresh token TTL in days. |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | JSON list of allowed CORS origins. |
| `ANGEL_ONE_API_KEY` | No | — | Angel One broker API key (optional; app starts without it). |

---

## Running Tests

```bash
cd backend

# All tests
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Performance benchmarks
python -m pytest tests/performance/ -v -s

# Error handling scenarios
python -m pytest tests/integration/test_error_handling.py -v
```

---

## Running Nightly Jobs Manually

Each job can be triggered from the backend directory:

```bash
# Ingest AMFI mutual fund NAVs
python -m app.jobs.ingest_amfi

# Ingest equity index prices
python -m app.jobs.ingest_equity

# Ingest NPS returns
python -m app.jobs.ingest_nps

# Compute performance metrics (CAGR, Sharpe, etc.)
python -m app.jobs.compute_metrics

# Compute advisor scores
python -m app.jobs.compute_scores

# Historical NAV backfill via mfapi
python -m app.jobs.ingest_mfapi
```

The scheduler runs these jobs automatically overnight when the server is running:

| Job | Schedule |
|---|---|
| AMFI NAV ingestion | Daily at 23:30 IST |
| Equity index ingestion | Weekdays at 16:30 IST |
| NPS returns ingestion | Mondays at 07:00 IST |
| Compute metrics | Daily at 01:00 IST |
| Compute advisor scores | Daily at 00:00 IST |
| mfapi historical backfill | Sundays at 02:00 IST |

---

## Health Check

```bash
curl http://localhost:8000/health
# {"status": "ok", "db": "connected", "scheduler": "running"}
```
