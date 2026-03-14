---
title: "Phase 5: Integration & Validation"
status: completed
version: "1.0"
phase: 5
---

# Phase 5: Integration & Validation

## Phase Context

**GATE**: Phases 1–4 must all be complete before starting this phase.

**Specification References**:
- `[ref: PRD/Success Metrics]` — all KPIs
- `[ref: PRD/Feature 1–4 Acceptance Criteria]` — 12 Gherkin criteria
- `[ref: SDD/Acceptance Criteria]` — EARS system-level criteria
- `[ref: SDD/Quality Requirements]` — measurable thresholds

**Dependencies**:
- Phase 1 complete (dark mode token migration)
- Phase 2 complete (AMFI fix)
- Phase 3 complete (mfapi fix)
- Phase 4 complete (NPS fix)

---

## Tasks

Validates the complete feature end-to-end: dark mode visual consistency, all three ingestion jobs functional, no regressions in tests or type checking.

---

- [ ] **T5.1 Full test suite — backend** `[activity: validate]`

  1. **Prime**: Review `[ref: SDD/Acceptance Criteria]` for backend criteria.
  2. **Test**: `cd backend && pytest` — all tests must pass.
  3. **Implement**: Fix any test failures caused by the Phase 2–4 changes (e.g., test mocks that need updating for new `headers` parameter or new function signatures).
  4. **Validate**: `pytest` exits with 0 failures, 0 errors.
  5. **Success**: Full backend test suite green. `[ref: PRD/Success Metrics]`

---

- [ ] **T5.2 Full test suite — frontend** `[activity: validate]`

  1. **Prime**: Review `[ref: SDD/Acceptance Criteria]` for frontend criteria.
  2. **Test**: `cd frontend && npm test && npm run typecheck && npm run lint` — all must pass.
  3. **Implement**: Fix any Vitest failures caused by Phase 1 class changes (snapshot tests may need updating; semantic token strings differ from hardcoded ones).
  4. **Validate**: All commands exit cleanly.
  5. **Success**: Full frontend test suite green, no type errors, no lint warnings. `[ref: PRD/Success Metrics]`

---

- [ ] **T5.3 Dark mode visual regression check** `[activity: frontend-ui]`

  1. **Prime**: Review all 6 PRD Gherkin criteria for Feature 1 `[ref: PRD/AC-1.1 through AC-1.6]`.
  2. **Test**: Open the dev server (`npm run dev`). Toggle dark mode on. Systematically visit each affected area.
  3. **Implement**: No implementation — this is verification. If any issue found, fix in the relevant Phase 1 task file before marking this task complete.
  4. **Validate**: Manual checklist:
     - [ ] Risk Profiler questionnaire: dark card backgrounds, no white surfaces `[ref: PRD/AC-1.1]`
     - [ ] Admin Job Dashboard: status badges legible in dark; table rows visible `[ref: PRD/AC-1.2]`
     - [ ] SIP Modeler: dark wrapper, themed summary cards, chart grid visible `[ref: PRD/AC-1.3]`
     - [ ] Stress Test: dark wrapper, asset allocation panel, chart grid visible `[ref: PRD/AC-1.3]`
     - [ ] Product Pins: dark panel, legible text `[ref: PRD/AC-1.4]`
     - [ ] Filter Summary: legible labels and values `[ref: PRD/AC-1.5]`
     - [ ] Switch back to light mode: all 7 components visually unchanged from pre-fix `[ref: PRD/AC-1.6]`
  5. **Success**: Zero hardcoded light-only color classes remaining in the 7 components. `[ref: PRD/Success Metrics — Dark Mode Coverage]`

---

- [ ] **T5.4 Ingestion jobs end-to-end smoke test** `[activity: validate]`

  1. **Prime**: Review `[ref: PRD/AC-2.1, AC-3.1, AC-4.1]` — minimum row count thresholds.
  2. **Test**: Run each job manually and observe structured log output.
  3. **Implement**: No implementation — this is verification. If any job fails, return to the relevant phase.
  4. **Validate**:
     - [ ] `python -m app.jobs.ingest_amfi` → `amfi_job_complete` with `inserted + skipped >= 1000` `[ref: PRD/AC-2.1]`
     - [ ] `python -m app.jobs.ingest_mfapi` → cursor file written; `inserted >= 1` (or progress logged) `[ref: PRD/AC-3.1]`
     - [ ] `python -m app.jobs.ingest_nps` → `nps_job_complete` with `inserted + updated >= 15` `[ref: PRD/AC-4.1]`
     - [ ] None of the three jobs crashes the scheduler (all errors are caught in `run()`) `[ref: PRD/AC-2.3, AC-4.2]`
  5. **Success**: All three ingestion jobs complete with non-zero record counts and no uncaught exceptions. `[ref: PRD/Success Metrics — AMFI/mfapi/NPS Job Success Rate]`

---

- [ ] **T5.5 Update spec README** `[activity: validate]`

  Mark `plan/` as `completed` in `.start/specs/005-dark-mode-and-ingestion-fixes/README.md`. Update `Current Phase` to `Ready`.

  Success: Spec README reflects implementation-ready status.
