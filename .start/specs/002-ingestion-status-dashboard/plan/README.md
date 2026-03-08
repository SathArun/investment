---
title: "Ingestion Status Dashboard"
status: draft
version: "1.0"
---

# Implementation Plan

## Validation Checklist

### CRITICAL GATES (Must Pass)

- [x] All `[NEEDS CLARIFICATION: ...]` markers have been addressed
- [x] All specification file paths are correct and exist
- [x] Each phase follows TDD: Prime → Test → Implement → Validate
- [x] Every task has verifiable success criteria
- [x] A developer could follow this plan independently

### QUALITY CHECKS (Should Pass)

- [x] Context priming section is complete
- [x] All implementation phases are defined with linked phase files
- [x] Dependencies between phases are clear (no circular dependencies)
- [x] Parallel work is properly tagged with `[parallel: true]`
- [x] Activity hints provided for specialist selection `[activity: type]`
- [x] Every phase references relevant SDD sections
- [x] Every test references PRD acceptance criteria
- [x] Integration & E2E tests defined in final phase
- [x] Project commands match actual project setup

---

## Context Priming

*GATE: Read all files in this section before starting any implementation.*

**Specification**:
- `.start/specs/002-ingestion-status-dashboard/requirements.md` — Product Requirements (PRD)
- `.start/specs/002-ingestion-status-dashboard/solution.md` — Solution Design (SDD)

**Key Design Decisions**:

- **ADR-1: Job tracking in scheduler.py** — Wrap each `_run_*()` function in `backend/app/jobs/scheduler.py` with `record_start` / `record_finish` calls. Individual job `run()` functions are unchanged except for a return value (int rows affected). All tracking logic lives in one place.
- **ADR-2: DB concurrency guard** — Before spawning a manual trigger thread, query `job_runs` for a `status='running'` row for that job. If found, return HTTP 409. No in-memory locks — state survives restarts.
- **ADR-3: Adaptive polling** — Frontend polls `GET /api/admin/jobs` every 5 seconds when any job is `running`, every 30 seconds otherwise. Interval recalculated on each response.
- **ADR-4: Prune on write** — After every `record_finish`, delete `job_runs` rows for that job beyond the 100 most recent. Keeps the table bounded without a separate cleanup job.

**Implementation Context**:

```bash
# Backend (run from backend/)
Dev:      uvicorn app.main:app --reload
Test:     pytest
Migrate:  alembic upgrade head

# Frontend (run from frontend/)
Dev:      npm run dev
Test:     npm test
Typecheck: npm run typecheck
Lint:     npm run lint
```

---

## Implementation Phases

Each phase is defined in a separate file. Tasks follow red-green-refactor: **Prime** (understand context), **Test** (red), **Implement** (green), **Validate** (refactor + verify).

> **Tracking Principle**: Track logical units that produce verifiable outcomes. The TDD cycle is the method, not separate tracked items.

- [x] [Phase 1: Database Foundation](phase-1.md)
- [x] [Phase 2: Backend Service & API](phase-2.md)
- [x] [Phase 3: Frontend Admin Page](phase-3.md)
- [x] [Phase 4: Dashboard Freshness Bar](phase-4.md)
- [x] [Phase 5: Integration & E2E Validation](phase-5.md)

---

## Plan Verification

| Criterion | Status |
|-----------|--------|
| A developer can follow this plan without additional clarification | ✅ |
| Every task produces a verifiable deliverable | ✅ |
| All PRD acceptance criteria map to specific tasks | ✅ |
| All SDD components have implementation tasks | ✅ |
| Dependencies are explicit with no circular references | ✅ |
| Parallel opportunities are marked with `[parallel: true]` | ✅ |
| Each task has specification references `[ref: ...]` | ✅ |
| Project commands in Context Priming are accurate | ✅ |
| All phase files exist and are linked from this manifest as `[Phase N: Title](phase-N.md)` | ✅ |
