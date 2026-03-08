---
title: "Phase 4: Dashboard Freshness Bar"
status: completed
version: "1.0"
phase: 4
---

# Phase 4: Dashboard Freshness Bar

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Secondary Flow — Dashboard freshness bar]` — wiring path: `fetchProducts` → `dashboardStore.dataFreshness` → `DataFreshnessBar` prop
- `[ref: SDD/Implementation Gotchas]` — "Verify exact field names in `data_freshness` from `GET /api/products` before wiring"
- `[ref: PRD/Feature 3]` — acceptance criteria for freshness bar display and stale warning
- `frontend/src/components/Dashboard/DataFreshness.tsx` — existing component (no changes needed)
- `frontend/src/store/dashboardStore.ts` — `dataFreshness` state already populated from `fetchProducts`
- `frontend/src/App.tsx` — `DashboardPage` where `DataFreshnessBar` is to be rendered

**Key Decisions**:
- The `DataFreshness` component is **complete and correct** — do not modify it. Only wire it.
- `dataFreshness` is already set in `dashboardStore` by the existing `fetchProducts` call — no new API endpoint needed.
- The freshness bar renders in the control bar area (below `AppNav`, above `FilterBar`), showing `amfi`, `equity`, `nps` timestamps.

**Dependencies**:
- Phase 1 complete (not strictly required for frontend, but must be done before full integration)
- Phase 2 complete: `GET /api/products` must include `data_freshness` field in response (verify this is already true in the existing backend before implementing)

---

## Tasks

Wires the existing `DataFreshnessBar` component into the dashboard, giving the advisor a passive staleness signal before client meetings.

- [ ] **T4.1 Verify data_freshness field names from GET /api/products** `[activity: backend-api]`

  1. Prime: Read `backend/app/market_data/service.py` — find where `data_freshness` is assembled. Read `backend/app/market_data/router.py` — find the `GET /api/products` response. Read `frontend/src/components/Dashboard/DataFreshness.tsx` — confirm it expects `{ amfi, equity, nps }` field names. Read `frontend/src/types/product.ts` — confirm `DataFreshness` type definition. `[ref: SDD/Implementation Gotchas]`
  2. Test: Write a test that calls `GET /api/products` with a valid JWT and asserts `data_freshness` is present in the response with field names `amfi`, `equity`, `nps` (each a string timestamp or null). If field names differ, the `DataFreshness` type in `types/product.ts` must be updated to match.
  3. Implement: No code changes expected if field names already match. If they differ: update `frontend/src/types/product.ts` `DataFreshness` interface to use the actual API field names. Update `DataFreshness.tsx` source keys accordingly (only if necessary — prefer matching API to component, not the reverse).
  4. Validate: `GET /api/products` response includes `data_freshness` with `amfi`, `equity`, `nps` keys (or corrected keys). TypeScript types match.
  5. Success:
     - [ ] `DataFreshness` TypeScript type matches actual API response shape `[ref: SDD/Implementation Gotchas]`

- [ ] **T4.2 Wire DataFreshnessBar into DashboardPage** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/App.tsx` `DashboardPage` function — identify where to add the freshness bar (below `AppNav` / `ClientViewToggle` bar, above `FilterBar`). Read `frontend/src/store/dashboardStore.ts` — confirm `dataFreshness` is accessible from store. Read `frontend/src/components/Dashboard/DataFreshness.tsx` — confirm `Props` interface. `[ref: SDD/Secondary Flow — Dashboard freshness bar]`
  2. Test: Write component tests for `DashboardPage` or the freshness bar area: (a) when `dataFreshness` is `null` (loading), the freshness bar shows a loading state or skeleton, not empty/broken; (b) when `dataFreshness` has timestamps within 48h, no ⚠ icons appear; (c) when any timestamp is older than 48h, the corresponding source shows a red ⚠ stale warning.
  3. Implement: In `App.tsx` `DashboardPage`: import `DataFreshnessBar` from `@/components/Dashboard/DataFreshness`; read `dataFreshness` from `useDashboardStore`; render `{dataFreshness && <DataFreshnessBar freshness={dataFreshness} />}` in the control bar section (alongside `ClientViewToggle`). For the loading state: show a simple `<span className="text-xs text-gray-400">Loading data status...</span>` when `isLoading && !dataFreshness`.
  4. Validate: `npm run typecheck` clean. Dashboard loads without errors. Freshness bar appears on the dashboard page. When `data_freshness` has a stale timestamp in dev, ⚠ indicator appears.
  5. Success:
     - [ ] Freshness bar visible on `/dashboard` showing AMFI, Equity, NPS last-update dates `[ref: PRD/Feature 3 AC — freshness bar visible on /dashboard]`
     - [ ] Sources updated within 48h show no warning icons `[ref: PRD/Feature 3 AC — all green when fresh]`
     - [ ] Sources older than 48h show red ⚠ stale indicator `[ref: PRD/Feature 3 AC — red stale warning]`
     - [ ] Loading state shows graceful placeholder, not empty dates `[ref: PRD/Feature 3 AC — loading state]`

- [ ] **T4.3 Phase 4 Validation** `[activity: validate]`

  - Run `npm test` — all existing dashboard tests still pass, new freshness tests pass. `npm run typecheck` clean. Open `/dashboard` in browser — freshness bar is visible. Confirm it reflects the timestamps from the most recent successful job runs.
