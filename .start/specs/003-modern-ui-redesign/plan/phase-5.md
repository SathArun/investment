---
title: "Phase 5: shadcn/ui Component Migration and Integration Tests"
status: completed
version: "1.0"
phase: 5
---

# Phase 5: shadcn/ui Component Migration and Integration Tests

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Building Block View — Directory Map; MODIFY files: LoginForm.tsx, JobCard.tsx]`
- `[ref: SDD/Implementation Boundaries — Can Modify list]`
- `[ref: PRD/Should Have Features — Button, Badge, Card, Input standardization]`
- `[ref: SDD/Quality Requirements — bundle size ≤ 50KB gzipped, all tests pass]`
- `[ref: SDD/Risks — ClientViewToggle.tsx deprecation]`
- `[ref: SDD/Acceptance Criteria — shadcn/ui Button used in LoginForm, FilterBar, JobCard]`

**Key Decisions**:
- Incremental migration: only LoginForm and JobCard migrated in this phase (highest value, lowest risk)
- FilterBar Select migration is "nice-to-have" — attempt only if LoginForm + JobCard complete cleanly
- `ClientViewToggle.tsx` deprecated but NOT deleted (existing tests may reference it); delete only after confirming no test imports
- Final integration test verifies the complete client view toggle flow end-to-end

**Dependencies**:
- All phases 1–4 complete
- All new components and layout from phases 2–4 stable

---

## Tasks

Migrates the highest-impact existing components to shadcn/ui primitives, deprecates the old ClientViewToggle, and runs the complete integration test suite to validate the full modern UI redesign.

- [ ] **T5.1 LoginForm migration to shadcn/ui Button + Input** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Login/LoginForm.tsx` fully; note all `<input>` and `<button>` elements and their current className strings `[ref: SDD/Building Block View — LoginForm.tsx MODIFY]`
  2. Test: Run existing `src/tests/` login tests — all must pass before and after migration; add assertion that `<Button>` and `<Input>` from `src/components/ui/` are rendered
  3. Implement: In `LoginForm.tsx`:
     - Replace `<input className="w-full border border-gray-300 ...">` with `<Input>` from `src/components/ui/input`
     - Replace `<button className="w-full bg-blue-600 ...">` with `<Button className="w-full">` from `src/components/ui/button`
     - Replace `<label className="...">` with `<Label>` if shadcn `label` component installed; otherwise keep native label
     - Preserve all existing `{...register(...)}` React Hook Form bindings
     - Preserve all error message rendering
  4. Validate: `npm test -- --run`; `npm run typecheck`; manual login flow works
  5. Success:
     - [ ] LoginForm renders shadcn/ui `Input` and `Button` `[ref: SDD/Acceptance Criteria]`
     - [ ] All existing login tests pass `[ref: SDD/Implementation Boundaries — Must Preserve]`
     - [ ] No visual regression in login form appearance `[ref: SDD/Quality Requirements]`

- [ ] **T5.2 JobCard migration to shadcn/ui Card + Badge** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Admin/JobCard.tsx` fully; note `<div className="bg-white rounded-lg border p-4...">` card container and status badge spans `[ref: SDD/Building Block View — JobCard.tsx MODIFY]`
  2. Test: Run existing `src/tests/JobCard.test.tsx` — all must pass before and after; add assertion that `Card` and `Badge` from `src/components/ui/` are rendered
  3. Implement: In `JobCard.tsx`:
     - Replace outer `<div className="bg-white rounded-lg border...">` with `<Card><CardContent>` from `src/components/ui/card`
     - Replace status badge `<span className="px-2 py-0.5 rounded text-xs bg-green-100...">` with `<Badge>` from `src/components/ui/badge`
     - Map status → badge variant: `success` → custom green, `failed` → `destructive`, `running` → custom blue, `never_run` → `secondary`
     - Preserve "Run Now" button and collapse toggle functionality
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] JobCard renders shadcn/ui `Card` and `Badge` `[ref: SDD/Acceptance Criteria]`
     - [ ] All existing JobCard tests pass `[ref: SDD/Implementation Boundaries]`
     - [ ] Status badge colors match original (success=green, failed=red, running=blue, never_run=gray) `[ref: SDD/Quality Requirements]`

- [ ] **T5.3 ClientViewToggle deprecation** `[activity: frontend-ui]`

  1. Prime: Run `grep -r "ClientViewToggle" frontend/src/` to find all imports; confirm ViewToggle is used everywhere ClientViewToggle was `[ref: SDD/Risks — ClientViewToggle deprecation]`
  2. Test: Verify no component imports `ClientViewToggle` after migration; ViewToggle renders in all places where ClientViewToggle previously appeared
  3. Implement:
     - If `ClientViewToggle.tsx` is imported nowhere: add `// @deprecated — replaced by ViewToggle` JSDoc comment and leave file for one more cycle
     - Remove import from any remaining files that still reference it
     - Confirm `ViewToggle` is the only view-mode toggle component rendered in the app
  4. Validate: `npm test -- --run`; `npm run typecheck`; `grep -r "ClientViewToggle" src/` returns 0 active imports
  5. Success:
     - [ ] Zero active imports of `ClientViewToggle` in src/ `[ref: SDD/Risks — deprecation]`
     - [ ] `ViewToggle` renders correctly in DashboardPage toolbar `[ref: Phase 3 T3.5]`

- [ ] **T5.4 Full integration test — client view toggle flow** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/tests/` for existing integration patterns; review all PRD Feature 2 acceptance criteria `[ref: PRD/Feature 2 — all 9 acceptance criteria; SDD/Runtime View — sequence diagram]`
  2. Test: Write `src/tests/ClientViewFlow.test.tsx` integration test:
     - Render `DashboardPage` with mock store (products loaded, pinned products present)
     - Assert advisor view initial state: FilterBar visible, all columns in table, ViewToggle shows "Advisor View" selected
     - Fire toggle to "Client View"
     - Assert: FilterSummary visible (FilterBar gone), 6 columns in table (Breakdown absent), ProductPins hero cards visible, sidebar collapsed (`isSidebarCollapsed=true`)
     - Fire "Change filters" link
     - Assert: back to Advisor View, FilterBar visible
  3. Implement: Write the integration test (test code, not feature code)
  4. Validate: `npm test -- --run` — all tests including new integration test pass
  5. Success:
     - [ ] Integration test covers full toggle flow (advisor → client → advisor) `[ref: PRD/Feature 2 all AC]`
     - [ ] All 9 client view AC verified programmatically `[ref: PRD/Feature 2 Acceptance Criteria]`

- [ ] **T5.5 Final build validation and bundle check** `[activity: validate]`

  1. Prime: Review PRD Success Metrics (bundle ≤ 50KB, CLS=0) and SDD Quality Requirements `[ref: PRD/Success Metrics; SDD/Quality Requirements]`
  2. Test: `npm run build` produces clean output; check bundle size delta
  3. Implement:
     - Run `npm run build`
     - Check `dist/assets/*.js` size — compare to pre-migration build size; delta must be ≤ 50KB gzipped
     - Run `npm test -- --run` — all tests pass (0 failures)
     - Run `npm run typecheck` — 0 errors
     - Run `npm run lint` — 0 errors
  4. Validate: All 4 quality gates pass
  5. Success:
     - [ ] `npm run build` succeeds with 0 errors `[ref: SDD/Quality Requirements]`
     - [ ] Bundle size increase ≤ 50KB gzipped `[ref: PRD/Constraints — ≤50KB]`
     - [ ] All tests pass (0 failures) `[ref: SDD/Quality Requirements — Reliability]`
     - [ ] 0 TypeScript errors, 0 lint errors `[ref: SDD/Quality Requirements]`

- [ ] **T5.6 Phase 5 Validation** `[activity: validate]`

  - Run full test suite: `npm test -- --run`.
  - Run `npm run typecheck && npm run lint && npm run build`.
  - Manual end-to-end walkthrough: Login → Dashboard (sidebar, collapse, advisor/client toggle) → Goals → Risk Profiler → Scenarios → Admin (skeleton loaders).
  - Verify all PRD acceptance criteria (Features 1–4) are met in browser.
  - Check Inter font renders in browser DevTools computed styles.
  - Check `sidebar_collapsed` persists in localStorage across page refresh.
