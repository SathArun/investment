---
title: "Phase 3: Final Validation"
status: completed
version: "1.0"
phase: 3
---

# Phase 3: Final Validation

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Acceptance Criteria — all 16 criteria]`
- `[ref: SDD/Quality Requirements]`
- `[ref: SDD/Runtime View — Primary Flow: Theme Toggle; Primary Flow: Initial Load]`

**Key Decisions**:
- All 16 acceptance criteria must be verified
- Recharts chart dark-prop updates are verified during dark mode toggle
- localStorage persistence tested via reload simulation

**Dependencies**:
- Phase 1 complete (uiStore, dark class, layout)
- Phase 2 complete (all component token migrations)

---

## Tasks

Final end-to-end validation of the complete dark modernization against all SDD acceptance criteria.

- [ ] **T3.1 Full test suite + build verification** `[activity: validate]`

  1. Prime: Read `SDD/Acceptance Criteria` — all 16 criteria `[ref: SDD/Acceptance Criteria]`
  2. Test: Write `src/tests/DarkModeIntegration.test.tsx`:
     - On initial render with no localStorage key: `document.documentElement.classList.contains('dark')` = true
     - On initial render with localStorage 'theme'='light': `dark` class absent
     - Toggle from dark → light: class removed from html, `isDarkMode` = false, localStorage = 'light'
     - Toggle from light → dark: class added, `isDarkMode` = true, localStorage = 'dark'
     - SidebarFooter: Moon shown in dark, Sun shown in light
     - Theme toggle button `aria-label` correct in each state
  3. Implement: Write the integration test (test code, not feature code)
  4. Validate:
     - `npm run test -- --run` — all tests pass including new integration test
     - `npm run typecheck` — 0 errors
     - `npm run lint` — 0 errors
     - `npm run build` — clean build

- [ ] **T3.2 Phase 3 Validation** `[activity: validate]`

  - Run full suite: `npm run test -- --run`. `npm run typecheck`. `npm run lint`. `npm run build`.
  - Manual end-to-end:
    1. Open app — verify dark mode active by default.
    2. Click Moon button in sidebar footer — page switches to light mode.
    3. Reload page — light mode persists.
    4. Click Sun button — dark mode restored. Reload — dark persists.
    5. Navigate all routes: Dashboard, Goals, Risk Profiler, Scenarios, Admin — all content areas dark.
    6. Dashboard → switch to Client View — FilterSummary, AssetTable, ProductPins all dark.
    7. Goals page on wide screen — GoalForm two-column layout visible.
    8. Open ScoreBreakdown panel — dark card background (not white).
    9. Check Recharts on Dashboard — CartesianGrid lines visible on dark background.
    10. Check FilterBar dropdowns — dark popup background.
  - Verify all 16 SDD acceptance criteria are met.
