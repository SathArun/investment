---
title: "Dark Mode Completion and Data Ingestion Recovery"
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

## Specification Compliance Guidelines

### Deviation Protocol

When implementation requires changes from the specification:
1. Document the deviation with clear rationale
2. Obtain approval before proceeding
3. Update SDD when the deviation improves the design
4. Record all deviations in this plan for traceability

---

## Context Priming

*GATE: Read all files in this section before starting any implementation.*

**Specification**:
- `.start/specs/005-dark-mode-and-ingestion-fixes/requirements.md` — Product Requirements
- `.start/specs/005-dark-mode-and-ingestion-fixes/solution.md` — Solution Design (token map, job fix specs, ADRs)

**Key Design Decisions**:
- **ADR-1**: Dark mode via `dark:` Tailwind prefix — swap hardcoded gray/white to semantic tokens; add `dark:` variants for colored elements.
- **ADR-2**: Chart grid stroke — replace `stroke="#f0f0f0"` with `stroke="hsl(var(--border))"`.
- **ADR-3**: NPS two-path — attempt live JSON endpoint (Path A); fall back to `nps_returns_seed.json` (Path B).
- **ADR-4**: mfapi cursor — `data/mfapi_cursor.txt` persists last processed scheme_code; 500-scheme batch cap.
- **ADR-5**: No shared retry utility — per-job handling.

**Implementation Context**:
```bash
# Frontend (from frontend/)
npm test              # Vitest component tests
npm run typecheck     # TypeScript type check
npm run lint          # ESLint
npm run dev           # Dev server (visual verification)

# Backend (from backend/)
pytest                                    # All tests
python -m app.jobs.ingest_amfi            # Manual AMFI run
python -m app.jobs.ingest_mfapi           # Manual mfapi run
python -m app.jobs.ingest_nps             # Manual NPS run
```

---

## Implementation Phases

Each phase is defined in a separate file. Tasks follow red-green-refactor: **Prime** (understand context), **Test** (red), **Implement** (green), **Validate** (refactor + verify).

> **Note**: Phases 1–4 are independent and can run in parallel. Phase 5 requires all prior phases complete.

- [x] [Phase 1: Dark Mode Token Migration](phase-1.md)
- [x] [Phase 2: AMFI Ingestion Fix](phase-2.md)
- [x] [Phase 3: mfapi Backfill Hardening](phase-3.md)
- [x] [Phase 4: NPS Data Source Fix](phase-4.md)
- [x] [Phase 5: Integration & Validation](phase-5.md)

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
| All phase files exist and are linked from this manifest | ✅ |
