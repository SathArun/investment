---
title: "Phase 2: Component Token Migrations"
status: completed
version: "1.0"
phase: 2
---

# Phase 2: Component Token Migrations

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Implementation Examples 5, 6, 7, 8, 9]`
- `[ref: SDD/Architecture Decisions — ADR-2, ADR-3, ADR-4]`
- `[ref: SDD/Acceptance Criteria — Content Area Appearance, Recharts, FilterBar, GoalForm Layout]`
- `[ref: SDD/Risks and Technical Debt — GoalForm native inputs, CorpusChart/AllocationPie, Tooltip.Arrow fill]`

**Key Decisions**:
- ADR-2: Replace `bg-white`/`bg-gray-*`/`text-gray-*` with semantic tokens from the token map (SDD Example 5)
- ADR-3: FilterBar raw Radix Select → shadcn `Select` from `src/components/ui/select.tsx`; all 3 handler functions preserved
- ADR-4: GoalForm two-column via `lg:grid lg:grid-cols-2 lg:gap-8`; right column has `mt-6 lg:mt-0`
- Recharts SVG props use `hsl(var(--token))` string literals (ADR-2 exception)

**Dependencies**:
- Phase 1 complete (uiStore `isDarkMode`, `dark` class applied to `<html>`, `bg-background` on AppShell)

---

## Tasks

Migrates all content-area components from hardcoded light colors to semantic dark-mode tokens. All tasks are independent of each other and can run in parallel.

- [ ] **T2.1 AssetTable token migration** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/Dashboard/AssetTable.tsx` fully; map all `bg-white`, `bg-gray-*`, `text-gray-*`, `border-gray-*` class strings to their token replacements from the token map `[ref: SDD/Example 5; SDD/Risks — Tooltip.Arrow fill]`
  2. Test: Update `src/tests/AssetTable.test.tsx`: in dark mode context, table body has no `bg-white` class; thead has `bg-muted` class; pinned row has `bg-yellow-500/10`; post-tax column has `bg-primary/10`; existing functionality (sort, pin, filter) tests still pass
  3. Implement: In `AssetTable.tsx` apply token map replacements (SDD Example 5):
     - `bg-white` → `bg-card` (tbody)
     - `bg-gray-50` → `bg-muted` (thead)
     - `hover:bg-gray-50` → `hover:bg-muted/50` (tr hover)
     - `text-gray-900` → `text-foreground`; `text-gray-700` → `text-muted-foreground`; `text-gray-500` → `text-muted-foreground`
     - `border-gray-200` → `border-border`; `divide-gray-100` → `divide-border`
     - `bg-yellow-50` → `bg-yellow-500/10`; `bg-blue-50` → `bg-primary/10`; `text-blue-800` → `text-primary`
     - `hover:bg-gray-100` → `hover:bg-muted` (header th hover)
     - Radix Tooltip.Content: `bg-white border-gray-200` → `bg-card border-border`; Tooltip text: `text-gray-500/text-gray-800` → `text-muted-foreground/text-foreground`
     - Tooltip.Arrow: `fill-white` → `fill-card` (or `style={{ fill: 'hsl(var(--card))' }}` if Tailwind fill-card not in bundle) `[ref: SDD/Gotchas 1]`
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] AssetTable renders with no hardcoded `bg-white`/`bg-gray-*` `[ref: SDD/AC — Content Area Appearance]`
     - [ ] All existing AssetTable tests pass (sort, pin, columns, skeleton) `[ref: SDD/AC — Preserved Behavior]`

- [ ] **T2.2 FilterBar → shadcn Select migration** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/Dashboard/FilterBar.tsx` fully; note the `SimpleSelect` component, the `@radix-ui/react-select` import, and the 3 handler functions `[ref: SDD/Example 7; SDD/ADR-3]`
  2. Test: Update `src/tests/FilterBar.test.tsx`: FilterBar renders shadcn `Select` (SelectTrigger/SelectContent) rather than raw Radix; all 3 `onValueChange` handlers fire correctly; post-tax notice has `bg-primary/10` class; existing FilterBar tests pass
  3. Implement: In `FilterBar.tsx`:
     - Remove `import * as Select from '@radix-ui/react-select'`
     - Add `import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'`
     - Rewrite `SimpleSelect` to use shadcn components (keep props interface identical) `[ref: SDD/Example 7]`
     - `label className`: `text-gray-600` → `text-muted-foreground`
     - Post-tax notice div: `bg-blue-50 text-blue-700` → `bg-primary/10 text-primary`
     - Note gotcha: check shadcn Select handles empty string value `[ref: SDD/Gotchas 1]`
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] FilterBar uses shadcn Select component `[ref: SDD/AC — FilterBar]`
     - [ ] All 3 handler functions (`handleTaxBracketChange`, `handleTimeHorizonChange`, `handleRiskFilterChange`) preserved `[ref: SDD/AC — FilterBar; SDD/CON-5]`
     - [ ] FilterBar tests pass `[ref: SDD/AC — Preserved Behavior]`

- [ ] **T2.3 RiskReturnPlot Recharts dark props + tooltip token migration** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/Dashboard/RiskReturnPlot.tsx` fully; identify CartesianGrid, XAxis, YAxis props and CustomTooltip component `[ref: SDD/Example 6; SDD/ADR-2]`
  2. Test: Update `src/tests/RiskReturnPlot.test.tsx`: RiskReturnPlot wrapper has `bg-card border-border` class; CustomTooltip renders `bg-card border-border text-foreground` classes; existing client/advisor view tests pass
  3. Implement: In `RiskReturnPlot.tsx`:
     - Chart wrapper div: `bg-white rounded-lg border` → `bg-card rounded-lg border border-border`
     - `CartesianGrid`: add `stroke="hsl(var(--border))"`
     - `XAxis`: add `tick={{ fill: 'hsl(var(--muted-foreground))' }}` and `label={{ ...existing..., fill: 'hsl(var(--muted-foreground))' }}`
     - `YAxis`: same pattern
     - `CustomTooltip`: `bg-white border border-gray-200` → `bg-card border border-border`; tooltip text classes → `text-foreground`/`text-muted-foreground`
     - Chart heading: `text-gray-700` → `text-muted-foreground`
     - CATEGORY_COLORS map: do NOT change (data-series colors, not UI tokens) `[ref: SDD/Example 6]`
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] CartesianGrid uses `hsl(var(--border))` stroke `[ref: SDD/AC — Recharts]`
     - [ ] Axis tick labels use `hsl(var(--muted-foreground))` fill `[ref: SDD/AC — Recharts]`
     - [ ] CustomTooltip renders with dark-aware classes `[ref: SDD/AC — Recharts]`
     - [ ] Existing RiskReturnPlot tests pass (client/advisor view) `[ref: SDD/AC — Preserved Behavior]`

- [ ] **T2.4 ScoreBreakdown token migration** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/Dashboard/ScoreBreakdown.tsx` fully; map all ~12 hardcoded color classes `[ref: SDD/Example 9; SDD/Acceptance Criteria — Content Area Appearance]`
  2. Test: Update `src/tests/ScoreBreakdown.test.tsx`: Dialog.Content panel has `bg-card` class (not `bg-white`); composite score section has `bg-muted`; close button hover has `hover:bg-muted`; existing open/close/render tests pass
  3. Implement: In `ScoreBreakdown.tsx` apply the full token migration from SDD Example 9:
     - Dialog.Content: `bg-white` → `bg-card`
     - Header: `border-gray-200` → `border-border`; `text-gray-900` → `text-foreground`; `text-gray-500` → `text-muted-foreground`
     - Close button: `hover:bg-gray-100` → `hover:bg-muted`; `text-gray-400` → `text-muted-foreground`; `hover:text-gray-600` → `hover:text-foreground`
     - Composite score section: `bg-gray-50 border-gray-200` → `bg-muted border-border`; `text-gray-600` → `text-muted-foreground`; `text-gray-900` → `text-foreground`
     - Score track: `bg-gray-200` → `bg-muted`
     - Sub-score heading: `text-gray-400` → `text-muted-foreground`
     - Per sub-score: `text-gray-800` → `text-foreground`; `text-gray-400` → `text-muted-foreground`; `text-gray-700` → `text-foreground`; `bg-gray-100` → `bg-muted`
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] ScoreBreakdown panel renders `bg-card` background `[ref: SDD/AC — Content Area Appearance]`
     - [ ] All sub-score sections use muted tokens `[ref: SDD/Example 9]`
     - [ ] Existing ScoreBreakdown tests pass `[ref: SDD/AC — Preserved Behavior]`

- [ ] **T2.5 GoalForm token migration + two-column layout + native input dark mode** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/GoalPlanner/GoalForm.tsx` fully; identify the `space-y-6` outer wrapper, the form section, the results section, and all `bg-blue-50`/`bg-white`/`text-gray-*` classes; also read `src/components/GoalPlanner/CorpusChart.tsx` and `src/components/GoalPlanner/AllocationPie.tsx` to check if they contain Recharts elements needing dark props `[ref: SDD/Example 8; SDD/Risks — CorpusChart/AllocationPie]`
  2. Test: Update `src/tests/GoalPlanner.test.tsx`: on lg viewport, form and results render side-by-side (two-column grid class present); form card has `bg-card border-border`; result cards have `bg-card border-border`; NPS banner has `bg-primary/10 text-primary`; existing submit/validation tests pass
  3. Implement: In `GoalForm.tsx`:
     - Outer wrapper: `space-y-6` → `lg:grid lg:grid-cols-2 lg:gap-8` `[ref: SDD/Example 8]`
     - Right results column wrapper: add `mt-6 lg:mt-0` `[ref: SDD/Gotchas 4]`
     - Form card: `bg-white border` → `bg-card border border-border`
     - Form heading: `text-gray-800` → `text-foreground`
     - Labels: `text-gray-700` → `text-foreground` (primary labels); `text-gray-600` → `text-muted-foreground` (secondary)
     - Native inputs: add `bg-background text-foreground border-border focus:ring-ring` to each input className `[ref: SDD/Risks — native inputs]`
     - Add client panel: `bg-blue-50 border-blue-200 text-blue-700` → `bg-primary/10 border-primary/30 text-primary`
     - Result cards: `bg-white border` → `bg-card border border-border`; value text: `text-gray-900` → `text-foreground`; labels: `text-gray-500` → `text-muted-foreground`
     - NPS banner: `bg-blue-50 border-blue-200 text-blue-800` → `bg-primary/10 border-primary/30 text-primary`
     - Note: check SDD Gotcha 2 — `text-primary` in dark mode is near-white; if contrast is insufficient use `dark:text-blue-400`
     - Apply same Recharts dark props to CorpusChart/AllocationPie if they contain CartesianGrid/XAxis/YAxis `[ref: SDD/Risks — CorpusChart gotcha]`
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] GoalForm two-column on lg screens `[ref: SDD/AC — GoalForm Layout]`
     - [ ] GoalForm single-column on < lg screens `[ref: SDD/AC — GoalForm Layout]`
     - [ ] No hardcoded `bg-white`/`bg-blue-50` in GoalForm `[ref: SDD/AC — Content Area Appearance]`
     - [ ] Native inputs readable in dark mode `[ref: SDD/Risks — native inputs]`
     - [ ] Existing GoalPlanner tests pass `[ref: SDD/AC — Preserved Behavior]`

- [ ] **T2.6 FilterSummary token migration** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/Dashboard/FilterSummary.tsx` — 3 token replacements `[ref: SDD/Example 5; SDD/Building Block View — FilterSummary.tsx MODIFY]`
  2. Test: FilterSummary renders `text-muted-foreground` outer text, `text-foreground` filter value spans, `text-primary` for the "Change filters" link; existing FilterSummary tests pass
  3. Implement: In `FilterSummary.tsx`:
     - `text-gray-600` → `text-muted-foreground` (outer text)
     - `text-gray-800` → `text-foreground` (filter value spans)
     - `text-blue-600` → `text-primary` (Change filters link)
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] FilterSummary uses token classes `[ref: SDD/Example 5]`
     - [ ] Existing FilterSummary tests pass `[ref: SDD/AC — Preserved Behavior]`

- [ ] **T2.7 Phase 2 Validation** `[activity: validate]`

  - Run `npm run test -- --run`. Run `npm run typecheck`. Run `npm run build`.
  - Manual check: switch to dark mode (isDarkMode=true) — verify no `bg-white` surfaces visible in content area.
  - Manual check: GoalForm two-column renders on wide screen.
  - Manual check: FilterBar dropdowns open with dark background.
