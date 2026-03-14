---
title: "Phase 1: Dark Mode Token Migration"
status: completed
version: "1.0"
phase: 1
---

# Phase 1: Dark Mode Token Migration

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Tailwind Token Substitution Map]` — authoritative class substitution table
- `[ref: SDD/Status Badge Dark Variants]` — badge color dark: additions
- `[ref: SDD/SIPModeler Summary Card Dark Variants]` — summary card dark: additions
- `[ref: SDD/Chart Grid Stroke Fix]` — CartesianGrid stroke replacement
- `[ref: PRD/Feature 1 — Full Dark Mode Coverage]` — 6 Gherkin acceptance criteria

**Key Decisions**:
- ADR-1: `dark:` Tailwind prefix; semantic tokens for gray/white; `dark:` variants for colored elements.
- ADR-2: `stroke="hsl(var(--border))"` for Recharts CartesianGrid (both SIPModeler and StressTest).
- Light-mode appearance must be visually unchanged.

**Dependencies**:
- None. This phase is fully independent of Phases 2–4.

---

## Tasks

Delivers fully dark-mode-compatible versions of all 7 components. No logic changes — CSS class strings only.

---

- [ ] **T1.1 Questionnaire dark mode** `[activity: frontend-ui]` `[parallel: true]`

  1. **Prime**: Read `frontend/src/components/RiskProfiler/Questionnaire.tsx`. Review SDD token map `[ref: SDD/Tailwind Token Substitution Map]`.
  2. **Test**: In dark mode (add `dark` class to `<html>` in browser), question card backgrounds should be `bg-card` (not white); labels should use `text-muted-foreground`; borders should use `border-border`. Verify light mode looks identical to today.
  3. **Implement**: Apply substitutions throughout `Questionnaire.tsx`:
     - `text-gray-500` → `text-muted-foreground` (loading paragraph)
     - `text-gray-700` (label, option text) → `text-muted-foreground`
     - `border-gray-300` → `border-border` (select, inputs)
     - `border-gray-200` → `border-border` (question cards, result card)
     - `bg-white` → `bg-card` (question card `p-4`, result card `p-6`)
     - `text-gray-800` → `text-foreground` (question text)
     - `text-gray-900` → `text-foreground` (result heading)
     - `text-gray-600` → `text-muted-foreground` (risk description)
  4. **Validate**: `npm run typecheck && npm run lint` pass. In browser: dark mode shows dark card backgrounds; light mode unchanged.
  5. **Success**: Given dark mode active, Questionnaire renders with dark card surfaces and muted text — no white backgrounds visible. `[ref: PRD/AC-1.1]`

---

- [ ] **T1.2 JobCard + RunHistoryTable dark mode** `[activity: frontend-ui]` `[parallel: true]`

  1. **Prime**: Read `frontend/src/components/Admin/JobCard.tsx` and `RunHistoryTable.tsx`. Review SDD status badge dark variants `[ref: SDD/Status Badge Dark Variants]`.
  2. **Test**: In dark mode: job name text visible (not dark-on-dark); success badge shows green-on-dark-green; failed badge shows red-on-dark-red; running badge shows blue-on-dark-blue; table row text visible.
  3. **Implement**:
     - **JobCard.tsx**: `text-gray-900` → `text-foreground`; `text-gray-500` → `text-muted-foreground`. Add `dark:` variants to `StatusBadge`:
       - success: append `dark:bg-green-900/30 dark:text-green-400 dark:hover:bg-green-900/30`
       - failed: append `dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/30`
       - running: append `dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-900/30`
     - **RunHistoryTable.tsx**: `text-gray-500` → `text-muted-foreground` (thead); `text-gray-600` → `text-muted-foreground` (table cells). Add `dark:` variants to `StatusBadge` spans (same color pattern as above but using `-700` → `-400` shift).
  4. **Validate**: `npm run typecheck && npm run lint` pass. In browser dark mode: all badge colors legible; table text visible.
  5. **Success**: Given dark mode active, Admin Job Dashboard renders status badges in dark-compatible colors. `[ref: PRD/AC-1.2]`

---

- [ ] **T1.3 SIPModeler dark mode** `[activity: frontend-ui]` `[parallel: true]`

  1. **Prime**: Read `frontend/src/components/ScenarioPlanner/SIPModeler.tsx`. Review SDD summary card dark variants and chart stroke fix `[ref: SDD/SIPModeler Summary Card Dark Variants]` `[ref: SDD/Chart Grid Stroke Fix]`.
  2. **Test**: In dark mode: outer card not white; input labels visible; summary cards readable; Recharts grid lines visible (not invisible `#f0f0f0` on dark background); Tooltip not white-on-dark.
  3. **Implement**:
     - Outer wrapper: `bg-white rounded-lg border p-6` → `bg-card rounded-lg border p-6`
     - `text-gray-800` (h2) → `text-foreground`
     - All label `text-gray-700` → `text-muted-foreground`
     - All input `border-gray-300` → `border-border`
     - Summary card "Total Invested": `bg-gray-50` → `bg-muted`; `text-gray-500` → `text-muted-foreground`; `text-gray-800` → `text-foreground`
     - Summary card "Base rate": keep `bg-blue-50 text-blue-700`; add `dark:bg-blue-900/20 dark:text-blue-300`; `text-blue-500` → `text-blue-500 dark:text-blue-400`
     - Summary card "Comparison": keep `bg-orange-50 text-orange-700`; add `dark:bg-orange-900/20 dark:text-orange-300`; `text-orange-500` → `text-orange-500 dark:text-orange-400`
     - Summary card "Extra gains": keep `bg-green-50 text-green-700`; add `dark:bg-green-900/20 dark:text-green-300`
     - `CustomTooltip` div: `bg-white border border-gray-200` → `bg-card border border-border`; `text-gray-700` → `text-foreground`
     - CartesianGrid: `stroke="#f0f0f0"` → `stroke="hsl(var(--border))"`
  4. **Validate**: `npm run typecheck && npm run lint` pass. In browser dark mode: all cards themed; chart grid visible; tooltip dark. Light mode: visually unchanged.
  5. **Success**: Given dark mode active, SIPModeler renders all cards and text using dark theme tokens; chart grid visible. `[ref: PRD/AC-1.3]`

---

- [ ] **T1.4 StressTest dark mode** `[activity: frontend-ui]` `[parallel: true]`

  1. **Prime**: Read `frontend/src/components/ScenarioPlanner/StressTest.tsx`. Review SDD chart stroke fix `[ref: SDD/Chart Grid Stroke Fix]`.
  2. **Test**: In dark mode: outer card not white; asset allocation panel not white; heading and labels visible; chart grid visible.
  3. **Implement**:
     - Outer wrapper: `bg-white rounded-lg border p-6 space-y-6` → `bg-card rounded-lg border p-6 space-y-6`
     - `text-gray-800` (h2) → `text-foreground`
     - Allocation panel: `bg-gray-50 rounded-lg p-4 space-y-4` → `bg-muted rounded-lg p-4 space-y-4`
     - `text-gray-700` (h3 "Asset Allocation") → `text-muted-foreground`
     - `text-gray-600` (slider labels) → `text-muted-foreground`
     - `text-gray-600` (loading span) → `text-muted-foreground`
     - Recovery chart title `text-gray-700` → `text-muted-foreground`
     - CartesianGrid: `stroke="#f0f0f0"` → `stroke="hsl(var(--border))"`
     - Note: scenario severity cards (`getSeverityColor`) use dynamic color classes — these already have contextual backgrounds (red/orange/amber/lime) that remain appropriate in dark mode. No change needed for severity cards.
  4. **Validate**: `npm run typecheck && npm run lint` pass. In browser dark mode: wrapper and panel themed; chart grid visible.
  5. **Success**: Given dark mode active, Scenario Planner (StressTest tab) uses dark theme tokens. `[ref: PRD/AC-1.3]`

---

- [ ] **T1.5 ProductPins dark mode** `[activity: frontend-ui]` `[parallel: true]`

  1. **Prime**: Read `frontend/src/components/Presentation/ProductPins.tsx`. Review SDD token map `[ref: SDD/Tailwind Token Substitution Map]`.
  2. **Test**: In dark mode: outer panel not white; headings and list items visible; empty-state text visible; select border visible.
  3. **Implement**:
     - Outer wrapper: `bg-white rounded-lg border p-4` → `bg-card rounded-lg border p-4`
     - `text-gray-800` (advisor view heading) → `text-foreground`
     - `text-gray-400` (empty state text, both views) → `text-muted-foreground`
     - `text-gray-700` (pinned product list items) → `text-muted-foreground`
     - `text-gray-600` (client label, both views) → `text-muted-foreground`
     - `border-gray-300` (select) → `border-border`
  4. **Validate**: `npm run typecheck && npm run lint` pass. In browser dark mode: panel surface dark; all text legible.
  5. **Success**: Given dark mode active, Product Pins panel uses dark theme tokens. `[ref: PRD/AC-1.4]`

---

- [ ] **T1.6 FilterSummary dark mode** `[activity: frontend-ui]` `[parallel: true]`

  1. **Prime**: Read `frontend/src/components/Dashboard/FilterSummary.tsx`. Review SDD token map `[ref: SDD/Tailwind Token Substitution Map]`.
  2. **Test**: In dark mode: filter summary text visible (not dark-gray-on-dark); bold values legible.
  3. **Implement**:
     - `text-gray-600` (outer span) → `text-muted-foreground`
     - `text-gray-800` (font-medium value spans) → `text-foreground`
  4. **Validate**: `npm run typecheck && npm run lint` pass. In browser dark mode: filter labels and values legible.
  5. **Success**: Given dark mode active, Filter Summary labels and values use dark theme tokens. `[ref: PRD/AC-1.5]`

---

- [ ] **T1.7 Phase 1 Validation** `[activity: validate]`

  Run `npm test && npm run typecheck && npm run lint` from `frontend/`. All must pass.

  Visual checklist (manual, dev server):
  - [ ] Toggle to dark mode — all 7 components show dark surfaces.
  - [ ] Toggle back to light mode — all 7 components look unchanged from pre-fix.
  - [ ] No white islands visible in dark mode across: Risk Profiler, Admin Job Dashboard, SIP Modeler, Stress Test, Product Pins, Filter Summary.
  - [ ] Status badges (success/failed/running) legible in dark mode.
  - [ ] Chart grid lines visible in dark mode in SIPModeler and StressTest.

  Success: Zero components retain hardcoded `bg-white`, `text-gray-*`, or `border-gray-*` without a semantic token or `dark:` override. `[ref: PRD/Success Metrics — Dark Mode Coverage]`
