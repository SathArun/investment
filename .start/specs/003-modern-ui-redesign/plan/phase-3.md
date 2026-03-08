---
title: "Phase 3: Dual-Audience Dashboard — ViewToggle, FilterSummary, AssetTable, RiskReturnPlot"
status: pending
version: "1.0"
phase: 3
---

# Phase 3: Dual-Audience Dashboard — ViewToggle, FilterSummary, AssetTable, RiskReturnPlot

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Implementation Examples — CLIENT_VIEW_COLUMNS allowlist]`
- `[ref: SDD/Implementation Examples — FilterSummary with Change filters link]`
- `[ref: SDD/Implementation Examples — ViewToggle segmented control]`
- `[ref: SDD/Application Data Models — CLIENT_VIEW_COLUMNS; ViewToggle props]`
- `[ref: SDD/Runtime View — Primary Flow: Advisor switches to Client View]`
- `[ref: SDD/Runtime View — Complex Logic: GetVisibleNavLinks]`
- `[ref: PRD/Feature 2 — Dual-Audience View Switch; all Acceptance Criteria]`
- `[ref: PRD/Detailed Feature Spec — Dual-Audience View Switch; Business Rules 1-5; Edge Cases]`

**Key Decisions**:
- ADR-4: `CLIENT_VIEW_COLUMNS` is an allowlist constant — columns not in the list are hidden in client view by default
- ViewToggle: `peer-checked` CSS-only segmented control using hidden `<input type="radio">` + `<fieldset>`; switching to Client View calls both `setClientView(true)` AND `setSidebarCollapsed(true)`
- FilterSummary: reads current filter values from dashboardStore; "Change filters" button calls `setClientView(false)` only (does not touch sidebar state)
- RiskReturnPlot: `isClientView` prop simplifies axis labels and hides Advisor Score bubble-size legend; chart remains visible

**Dependencies**:
- Phase 1 complete (uiStore `setClientView`, `setSidebarCollapsed`)
- Phase 2 complete (AppShell + Sidebar consuming `isClientView` for nav filtering)

---

## Tasks

Implements the core dual-audience feature: the ViewToggle segmented control triggers a cascade of layout changes across the Dashboard — FilterBar↔FilterSummary swap, AssetTable column filtering, RiskReturnPlot label simplification.

- [ ] **T3.1 ViewToggle segmented control** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Presentation/ClientViewToggle.tsx` (existing); read `frontend/src/store/uiStore.ts` `[ref: SDD/Implementation Examples — ViewToggle; SDD/Application Data Models — ViewToggle props]`
  2. Test: Write `src/tests/ViewToggle.test.tsx`: renders two options ("Advisor View", "Client View"); "Client View" option checked when `isClientView=true`; clicking "Client View" calls `setClientView(true)` AND `setSidebarCollapsed(true)`; clicking "Advisor View" calls `setClientView(false)` only (not `setSidebarCollapsed`)
  3. Implement: Create `src/components/Presentation/ViewToggle.tsx` using `peer-checked` pattern:
     - `<fieldset>` container with `bg-gray-100 rounded-lg p-1`
     - Two `<label>` + `<input type="radio" className="sr-only peer">` pairs
     - Active option: `peer-checked:bg-white peer-checked:text-gray-900 peer-checked:shadow-sm`
     - Inactive: `text-gray-600`
     - onChange for "Client View": `setClientView(true); setSidebarCollapsed(true)`
     - onChange for "Advisor View": `setClientView(false)` only
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] Segmented control CSS-only pill (no JS state) `[ref: SDD/Implementation Examples — ViewToggle]`
     - [ ] Switching to Client View collapses sidebar AND sets client view `[ref: PRD/AC Feature 2; SDD/Runtime View]`
     - [ ] Uses semantic `<fieldset>` + `<input type="radio" sr-only>` for accessibility `[ref: SDD/ADR — Accessibility]`

- [ ] **T3.2 FilterSummary component** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Dashboard/FilterBar.tsx` to understand filter state shape; read `frontend/src/store/dashboardStore.ts` for `taxBracket`, `timeHorizon`, `riskFilter` fields `[ref: SDD/Implementation Examples — FilterSummary]`
  2. Test: Write `src/tests/FilterSummary.test.tsx`: renders current filter values as text; renders "Change filters" link; clicking "Change filters" calls `setClientView(false)`; shows dashes when filter values are undefined
  3. Implement: Create `src/components/Dashboard/FilterSummary.tsx`:
     - Reads `taxBracket`, `timeHorizon`, `riskFilter` from dashboardStore
     - Formats: "Filtered: {taxBracketLabel} · {timeHorizonLabel} · {riskLabel}"
     - Fallback: "—" for any undefined value
     - "Change filters" button: `onClick={() => setClientView(false)}`; styled `text-blue-600 hover:underline`
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] Shows current filter values in plain text `[ref: PRD/AC Feature 2 — FilterSummary]`
     - [ ] "Change filters" switches back to Advisor View `[ref: PRD/Open Questions resolved — link back]`
     - [ ] Dashes rendered when filter values absent `[ref: SDD/Error Handling — FilterSummary]`

- [ ] **T3.3 AssetTable CLIENT_VIEW_COLUMNS allowlist** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Dashboard/AssetTable.tsx` fully to map all column definitions and render logic `[ref: SDD/Application Data Models — CLIENT_VIEW_COLUMNS; SDD/Implementation Examples — AssetTable allowlist]`
  2. Test: Update `src/tests/AssetTable.test.tsx`: when `isClientView=true`, only CLIENT_VIEW_COLUMNS headers rendered; Breakdown button column absent; when `isClientView=false`, all columns visible including Breakdown
  3. Implement: In `AssetTable.tsx`:
     - Add `const CLIENT_VIEW_COLUMNS = ['name', 'sebi_risk_level', 'cagr_1y', 'cagr_3y', 'cagr_5y', 'post_tax_return_3y'] as const`
     - Compute `visibleColumns = isClientView ? ALL_COLUMNS.filter(col => CLIENT_VIEW_COLUMNS.includes(col.key)) : ALL_COLUMNS`
     - Apply `visibleColumns` to both `<thead>` and `<tbody>` rendering — no column takes space when hidden
     - The Breakdown button column key must NOT be in `CLIENT_VIEW_COLUMNS`
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] Client view renders exactly 6 columns (name, sebi_risk_level, cagr_1y, cagr_3y, cagr_5y, post_tax_return_3y) `[ref: PRD/AC Feature 2; SDD/ADR-4]`
     - [ ] Breakdown column absent in client view `[ref: PRD/AC Feature 2 — Breakdown hidden]`
     - [ ] All columns visible in advisor view (no regression) `[ref: SDD/Implementation Boundaries — Must Preserve]`
     - [ ] `CLIENT_VIEW_COLUMNS` constant is an exported const for testability `[ref: SDD/ADR-4]`

- [ ] **T3.4 RiskReturnPlot client view simplified labels** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Dashboard/RiskReturnPlot.tsx` fully; identify axis label text, legend/tooltip content, and Advisor Score reference `[ref: PRD/Open Questions resolved — simplify labels; SDD/Acceptance Criteria — RiskReturnPlot]`
  2. Test: Update `src/tests/RiskReturnPlot.test.tsx`: when `isClientView=true`, x-axis label is "Risk Level" (not raw metric name); y-axis label is "Annual Return"; Advisor Score bubble-size legend is not rendered; when `isClientView=false`, original labels present
  3. Implement: In `RiskReturnPlot.tsx`:
     - Accept `isClientView` from uiStore (or prop — follow existing pattern in file)
     - When `isClientView=true`: set x-axis label to "Risk Level", y-axis label to "Annual Return"
     - When `isClientView=true`: hide the legend/tooltip text referencing "Advisor Score" or bubble size
     - Keep chart visible in both views (no conditional unmount)
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] Simplified "Risk Level" / "Annual Return" axis labels in client view `[ref: PRD/Open Questions resolved]`
     - [ ] Advisor Score legend hidden in client view `[ref: PRD/AC Feature 2 — RiskReturnPlot]`
     - [ ] Chart remains fully visible in both views `[ref: PRD/Feature 2 — won't hide RiskReturnPlot]`

- [ ] **T3.5 DashboardPage layout wiring** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/App.tsx` `DashboardPage` component; understand how `FilterBar`, `ClientViewToggle`, `DataFreshnessBar`, `ProductPins` are currently composed `[ref: SDD/Building Block View — Components]`
  2. Test: Integration test `src/tests/DashboardPage.test.tsx`: renders ViewToggle toolbar; advisor view shows FilterBar; client view shows FilterSummary (not FilterBar); toolbar strip renders below AppShell nav
  3. Implement: Update `DashboardPage` in `App.tsx` (or extract to `src/pages/DashboardPage.tsx`):
     - Replace `ClientViewToggle` with `ViewToggle` component
     - Move `ViewToggle` to a toolbar strip (`bg-white border-b px-6 py-2 flex items-center justify-between`)
     - Conditionally render: `{isClientView ? <FilterSummary /> : <FilterBar />}`
     - Remove `DataFreshnessBar` from here (now in SidebarFooter)
     - Keep `{isClientView && <ProductPins />}` (ProductPins hero redesign in Phase 4)
  4. Validate: `npm test -- --run`; `npm run typecheck`; manual smoke in browser
  5. Success:
     - [ ] Advisor view: FilterBar visible, FilterSummary absent `[ref: PRD/AC Feature 2]`
     - [ ] Client view: FilterSummary visible with "Change filters" link, FilterBar absent `[ref: PRD/AC Feature 2]`
     - [ ] ViewToggle segmented control in toolbar strip `[ref: SDD/Cross-Cutting Concepts — UI Wireframe]`
     - [ ] No DataFreshnessBar in DashboardPage (moved to sidebar) `[ref: SDD/T2.3]`

- [ ] **T3.6 Phase 3 Validation** `[activity: validate]`

  - Run `npm test -- --run`. Run `npm run typecheck`. Run `npm run build`.
  - Manual end-to-end: toggle to Client View → sidebar collapses, FilterBar → FilterSummary, AssetTable 6 columns, RiskReturnPlot simplified. Click "Change filters" → Advisor View restored.
  - Verify Business Rules 1-5 from PRD Detailed Feature Spec.
