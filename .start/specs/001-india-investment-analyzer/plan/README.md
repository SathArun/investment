---
title: "India Investment Analyzer — Implementation Plan"
status: draft
version: "1.0"
---

# Implementation Plan

## Validation Checklist

### CRITICAL GATES (Must Pass)

- [x] All `[NEEDS CLARIFICATION]` markers have been addressed
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
- `.start/specs/001-india-investment-analyzer/requirements.md` — Product Requirements (PRD)
- `.start/specs/001-india-investment-analyzer/solution.md` — Solution Design (SDD)

**Key Design Decisions**:
- **ADR-1**: Modular Monolith — Single FastAPI + React deployable; no microservices
- **ADR-2**: SQLite Phase 1 — SQLAlchemy ORM + Alembic; PostgreSQL-compatible schema
- **ADR-3**: Pre-computed Nightly Scores — All 30,300 product×bracket×horizon combinations computed nightly; served from DB cache during the day
- **ADR-4**: ReportLab PDF — Pure Python; charts as embedded matplotlib PNGs
- **ADR-5**: WhatsApp via `wa.me` deep link — No WhatsApp Business API required
- **ADR-6**: Tax Rules as JSON Data — `data/reference/tax_rules.json` with `effective_from`/`effective_until` dates; modular update without code deploy
- **ADR-7**: React + Zustand + Recharts + Shadcn/ui — Lightweight state; React-native charts

**Implementation Context**:
```bash
# Backend (from /backend directory)
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
python -m app.db.migrate          # Create/migrate DB schema
python -m app.db.seed              # Seed reference data (tax rules, FD ranges, PPF rates)
python -m app.jobs.ingest_amfi     # Manual: fetch today's AMFI NAV
python -m app.jobs.compute_metrics # Manual: run nightly computation
pytest tests/                      # All tests
pytest tests/unit/                 # Unit tests only
pytest tests/integration/          # Integration tests

# Frontend (from /frontend directory)
npm install
npm run dev                        # Dev server on port 5173
npm run build                      # Production build
npm run typecheck                  # TypeScript check
npm run lint                       # ESLint
```

---

## Implementation Phases

Each phase is defined in a separate file. Tasks follow red-green-refactor: **Prime** (understand context), **Test** (red), **Implement** (green), **Validate** (refactor + verify).

> **Tracking Principle**: Track logical units that produce verifiable outcomes. The TDD cycle is the method, not separate tracked items.

- [x] [Phase 1: Project Foundation & Database](phase-1.md)
- [x] [Phase 2: Data Ingestion Layer](phase-2.md)
- [x] [Phase 3: Analytics Engine](phase-3.md)
- [x] [Phase 4: Score Engine & Market Data API](phase-4.md)
- [x] [Phase 5: Auth, Clients, Goals & Risk Profiler API](phase-5.md)
- [x] [Phase 6: PDF Generation Service](phase-6.md)
- [x] [Phase 7: React Dashboard & Core UI](phase-7.md)
- [x] [Phase 8: Goal Planner, Risk Profiler & Scenario UI](phase-8.md)
- [x] [Phase 9: Integration, E2E & Launch Readiness](phase-9.md)

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
