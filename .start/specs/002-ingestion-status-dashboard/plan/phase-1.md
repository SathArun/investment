---
title: "Phase 1: Database Foundation"
status: completed
version: "1.0"
phase: 1
---

# Phase 1: Database Foundation

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Data Storage Changes]` — `job_runs` table schema: columns, types, index
- `[ref: SDD/Application Data Models]` — `JobRun` SQLAlchemy Mapped[] entity definition
- `[ref: SDD/Implementation Gotchas]` — "Migration must run before app start" warning
- `backend/alembic/versions/0001_initial_schema.py` — existing migration to follow as structural template
- `backend/app/market_data/models.py` — canonical Mapped[] model pattern

**Key Decisions**:
- `job_runs` table uses `INTEGER PRIMARY KEY AUTOINCREMENT` (not UUID like other tables) for simple ordered pruning
- `status` is plain TEXT — validated at the application layer, not a DB enum
- Index on `(job_name, started_at DESC)` supports both the "last 10 per job" query and the "is running?" concurrency check

**Dependencies**:
- None. This phase has no upstream dependencies.

---

## Tasks

Establishes the persistence layer for job run history.

- [ ] **T1.1 Alembic migration 0002 — job_runs table** `[activity: data-architecture]`

  1. Prime: Read `backend/alembic/versions/0001_initial_schema.py` to understand migration file structure (imports, `upgrade()`, `downgrade()`, revision IDs). Read `SDD/Data Storage Changes` for exact column names and types. `[ref: SDD/Data Storage Changes]`
  2. Test: Write a test that runs `alembic upgrade head` against a fresh in-memory SQLite DB and asserts: (a) `job_runs` table exists, (b) all 7 columns are present with correct types, (c) `idx_job_runs_job_name_started` index exists.
  3. Implement: Create `backend/alembic/versions/0002_add_job_runs.py`. Set `revision = "0002"`, `down_revision = "0001"`. In `upgrade()`: create `job_runs` table with columns `id INTEGER PK AUTOINCREMENT`, `job_name TEXT NOT NULL`, `started_at DATETIME NOT NULL`, `finished_at DATETIME`, `status TEXT NOT NULL`, `rows_affected INTEGER`, `error_msg TEXT`. Create index `idx_job_runs_job_name_started` on `(job_name, started_at)`. In `downgrade()`: drop index then table.
  4. Validate: `alembic upgrade head` runs without error on a fresh DB. `alembic downgrade -1` then `alembic upgrade head` round-trips cleanly. Migration test passes.
  5. Success:
     - [ ] `alembic upgrade head` creates `job_runs` with all 7 specified columns `[ref: SDD/Data Storage Changes]`
     - [ ] `alembic downgrade -1` cleanly removes the table without affecting other tables `[ref: SDD/Data Storage Changes]`

- [ ] **T1.2 JobRun SQLAlchemy model** `[activity: domain-modeling]`

  1. Prime: Read `backend/app/market_data/models.py` for `Mapped[]` + `mapped_column()` pattern. Read `backend/app/db/base.py` for `Base` import. Review `SDD/Application Data Models` for the `JobRun` field list. `[ref: SDD/Application Data Models]`
  2. Test: Write a unit test that instantiates `JobRun(job_name="ingest_amfi", started_at=datetime.utcnow(), status="running")` and asserts: `__tablename__ == "job_runs"`, all fields are accessible, nullable fields (`finished_at`, `rows_affected`, `error_msg`) default to `None`.
  3. Implement: Create `backend/app/admin/__init__.py` (empty). Create `backend/app/admin/models.py` with `JobRun(Base)`: `id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)`, `job_name: Mapped[str]`, `started_at: Mapped[datetime]`, `finished_at: Mapped[datetime | None]`, `status: Mapped[str]`, `rows_affected: Mapped[int | None]`, `error_msg: Mapped[str | None]`. Use `from app.db.base import Base`.
  4. Validate: Unit test passes. `pytest backend/tests/` lint and typecheck clean.
  5. Success:
     - [ ] `JobRun` model reflects all columns from the 0002 migration with matching types `[ref: SDD/Application Data Models]`
     - [ ] Model can be instantiated without a DB session (pure Python object test) `[ref: SDD/Building Block View/Directory Map]`

- [ ] **T1.3 Phase 1 Validation** `[activity: validate]`

  - Run `alembic upgrade head` on a clean DB. Run `pytest` for migration and model tests. Confirm `job_runs` table structure matches SDD specification exactly. Verify `alembic downgrade -1` + `alembic upgrade head` round-trip succeeds.
