# Frontend UI Redesign — Architecture Overview

**Date**: 2026-03-09
**Status**: Implemented
**Scope**: `frontend/src/` only — no backend changes

---

## Summary

The Modern UI Redesign replaced the flat top-navigation shell with a collapsible dark sidebar layout, introduced shadcn/ui as the component primitive library, and added a dual-audience view mode for presenting investment data to end clients without exposing advisor-only data.

Key changes:

- **AppShell** — new flexbox layout shell (`AppShell.tsx`) replacing `AppNav`; sidebar + `flex-1` main content area
- **shadcn/ui** — copy-paste component library (Button, Badge, Card, Input, Select, Skeleton, Tooltip, Separator) added under `src/components/ui/`; CSS variable coexistence strategy (ADR-1)
- **Dual-audience view** — `isClientView` toggle in `uiStore` gates column visibility, nav items, FilterBar vs FilterSummary, and ProductPins hero layout
- **Skeleton loaders** — `<Skeleton>` rows in `AssetTable` and `JobCard` during data fetch; heights match content to achieve CLS=0
- **Inter font** — loaded via `@fontsource/inter`; tabular-nums variant applied to numeric table columns

---

## ADR-1: shadcn/ui Coexistence Strategy

**Date**: 2026-03-08
**Status**: Accepted

### Decision

shadcn/ui initialized with **New York style**, **Slate base color**, **CSS variables** mode. Only `--primary` is overridden:

```css
/* src/index.css */
:root {
  --primary: 219 90% 56%;   /* blue-600 equivalent */
}
```

New shadcn/ui components (`src/components/ui/`) use CSS variable references (`bg-primary`, `text-primary-foreground`). Existing feature components (`AssetTable`, `FilterBar`, etc.) retain direct Tailwind color classes (`bg-blue-600`, `text-gray-900`) unchanged.

### Rationale

Two token systems coexist during this phase. Zero migration risk — existing components are not touched. Full token consolidation is deferred to a later phase.

### Trade-offs

A developer adding a new component must choose which token system to use. Convention: use CSS variables in `src/components/ui/`, use direct Tailwind classes in feature components.

---

## ADR-2: Flexbox App Shell

**Date**: 2026-03-08
**Status**: Accepted

### Decision

`AppShell.tsx` uses `flex h-screen overflow-hidden` as the outer container. The sidebar uses `transition-[width] duration-300 ease-in-out` — **not** `transition-all`.

```tsx
// AppShell.tsx
<div className="flex h-screen overflow-hidden bg-gray-50">
  <aside className={cn(
    'bg-gray-900 flex flex-col shrink-0 transition-[width] duration-300 ease-in-out',
    isSidebarCollapsed ? 'w-16' : 'w-60'
  )}>
    {sidebar}
  </aside>
  <main id="main-content" className="flex-1 overflow-auto">
    {children}
  </main>
</div>
```

Sidebar dimensions: `w-60` (240px) expanded, `w-16` (64px) collapsed. `shrink-0` prevents the sidebar from being squeezed by flex layout.

### Why NOT `transition-all`

`transition-all` would also animate `opacity`, `color`, `box-shadow`, and any other property that changes during a re-render, causing unintended visual artifacts. `transition-[width]` restricts animation to the single property that needs it and is GPU-accelerated.

### Trade-offs

CSS Grid would offer more structured multi-panel layout control. Deferred if a third panel (e.g., detail drawer) is needed.

---

## ADR-3: Zustand uiStore Owns Sidebar Collapse

**Date**: 2026-03-08
**Status**: Accepted

### Decision

`isSidebarCollapsed: boolean` added to `uiStore`. Both write actions also write `localStorage`:

```ts
// uiStore.ts — initialization
isSidebarCollapsed: typeof window !== 'undefined'
  && localStorage.getItem('sidebar_collapsed') === 'true',

// toggleSidebar — flips state, writes localStorage
toggleSidebar: () => set((state) => {
  const next = !state.isSidebarCollapsed
  localStorage.setItem('sidebar_collapsed', String(next))
  return { isSidebarCollapsed: next }
}),

// setSidebarCollapsed — sets explicit value, writes localStorage
setSidebarCollapsed: (v: boolean) => {
  localStorage.setItem('sidebar_collapsed', String(v))
  set({ isSidebarCollapsed: v })
},
```

`localStorage` key: `sidebar_collapsed`. Read at store creation; defaults to `false` if absent.

When switching to Client View, `ViewToggle` calls `setClientView(true)` and `setSidebarCollapsed(true)` together. Switching back to Advisor View calls only `setClientView(false)` — the sidebar state is left as-is.

### Rationale

`uiStore` already owns `isClientView`; sidebar collapse is the same category of cross-component UI state. Global store is justified because the collapsed state affects multiple unrelated components (main content width, nav label visibility, DataFreshness placement).

### Trade-offs

UI state in a global store adds a dependency surface. Acceptable here given the multiple consumers.

---

## ADR-4: CLIENT_VIEW_COLUMNS Allowlist

**Date**: 2026-03-08
**Status**: Accepted

### Decision

`AssetTable.tsx` exports a `CLIENT_VIEW_COLUMNS` constant:

```ts
export const CLIENT_VIEW_COLUMNS = [
  'name', 'sebi_risk_level', 'cagr_1y', 'cagr_3y', 'cagr_5y', 'post_tax_return_3y',
] as const
```

When `isClientView=true`, the `visibleColumns` array is filtered against this allowlist before both `<thead>` and `<tbody>` render:

```ts
const visibleColumns = isClientView
  ? SORTABLE_COLUMNS.filter((col) =>
      (CLIENT_VIEW_COLUMNS as readonly string[]).includes(col.key)
    )
  : SORTABLE_COLUMNS
```

The `advisor_score` column and the `Breakdown` action column are excluded from the allowlist and are therefore absent in client view. Both `<thead>` and `<tbody>` are driven by `visibleColumns`, so hidden columns take zero DOM space.

### Rationale

Safe-by-default: any future column added to `SORTABLE_COLUMNS` is automatically hidden in client view until a developer explicitly adds its key to `CLIENT_VIEW_COLUMNS`. This prevents accidental advisor-only data exposure.

### Trade-offs

A developer adding a client-safe column must update `CLIENT_VIEW_COLUMNS`. This is intentional — the friction is a feature.

---

## Component Architecture

```
App (BrowserRouter)
└── ProtectedRoute
    └── AppShell (flex h-screen, <aside> + <main>)
        ├── Sidebar
        │   ├── Logo area (title hidden when collapsed)
        │   ├── SidebarNav (NavLinks with active state + left accent bar)
        │   │   ├── Advisor View: Dashboard, Goal Planner, Risk Profiler, Scenarios
        │   │   │   └── [separator] System Health (dim)
        │   │   └── Client View: Dashboard only
        │   ├── SidebarFooter (advisor name/email, DataFreshness, sign out)
        │   └── CollapseToggle button (ChevronLeft / ChevronRight)
        └── <Outlet /> (page content)
            └── DashboardPage
                ├── Toolbar
                │   └── ViewToggle (segmented control: Advisor View | Client View)
                ├── FilterBar (advisor view only)
                ├── FilterSummary (client view only; "Change filters" link)
                ├── ProductPins (hero card grid in client view)
                ├── AssetTable (CLIENT_VIEW_COLUMNS filter applied in client view)
                ├── RiskReturnPlot (advisor view only; simplified labels in client view)
                └── ScoreBreakdown (advisor view only)
```

### File Locations

| Component | Path |
|---|---|
| `AppShell` | `src/components/Layout/AppShell.tsx` |
| `Sidebar` | `src/components/Layout/Sidebar.tsx` |
| `SidebarNav` | `src/components/Layout/SidebarNav.tsx` |
| `SidebarFooter` | `src/components/Layout/SidebarFooter.tsx` |
| `ViewToggle` | `src/components/Presentation/ViewToggle.tsx` |
| `AssetTable` | `src/components/Dashboard/AssetTable.tsx` |
| `uiStore` | `src/store/uiStore.ts` |
| shadcn/ui primitives | `src/components/ui/` |
| `cn()` utility | `src/lib/utils.ts` |

---

## Dual-Audience View State Machine

`isClientView` in `uiStore` is the single source of truth for audience mode. It is presentation-only — no backend authorization changes.

### State transitions

| Trigger | Action | Sidebar effect |
|---|---|---|
| Click "Client View" in ViewToggle | `setClientView(true)` + `setSidebarCollapsed(true)` | Collapses to `w-16` |
| Click "Advisor View" in ViewToggle | `setClientView(false)` | No change (stays as-is) |
| Click "Change filters" in FilterSummary | `setClientView(false)` | No change |
| Click sidebar collapse toggle | `toggleSidebar()` | Flips; independent of view mode |

### Cascade when switching to Client View

1. `ViewToggle` calls `setClientView(true)` and `setSidebarCollapsed(true)`
2. `AppShell` re-renders: sidebar animates `w-60 → w-16` (300ms ease-in-out)
3. `SidebarNav` re-renders: only Dashboard link shown; Goal Planner, Risk Profiler, Scenarios, System Health hidden
4. `DashboardPage` re-renders: `FilterBar` unmounts; `FilterSummary` mounts with current filter values
5. `AssetTable` re-renders: `visibleColumns` filtered to `CLIENT_VIEW_COLUMNS`; Breakdown button absent
6. `ProductPins` re-renders as hero card grid (if pinned products exist)

### Cascade when switching back to Advisor View

1. `ViewToggle` or "Change filters" calls `setClientView(false)`
2. `SidebarNav` re-renders: full nav restored
3. `DashboardPage`: `FilterSummary` unmounts; `FilterBar` mounts
4. `AssetTable`: `visibleColumns` = all `SORTABLE_COLUMNS`; Breakdown button restored
5. Sidebar remains in whatever collapsed/expanded state it was last set to

---

## Known Issues / Future Work

These are identified from code review and the solution design:

1. **AdminPage polling reset bug** — The `useEffect` that sets the polling interval includes `jobs` in its dependency array. Because `jobs` is a new array reference on every fetch, the interval is cleared and reset on every poll cycle. Fix: move `jobs` out of the deps array or use a ref for the poll callback.

2. **ProductPins independent `/clients` fetch** — `ProductPins` fetches the `/clients` endpoint directly rather than reading from `goalStore`. This creates a duplicate fetch and diverges from the established store pattern. Fix: read pinned product data via `goalStore` or `dashboardStore`.

3. **ViewToggle does not restore sidebar on Advisor View switch** — Switching to Client View auto-collapses the sidebar (`setSidebarCollapsed(true)`). Switching back to Advisor View does not restore the sidebar to expanded. This is intentional per ADR-3 (sidebar state is independent after the initial collapse), but it may surprise users who expect the sidebar to reopen. If restoration is desired, `handleAdvisorView` in `ViewToggle` would need to call `setSidebarCollapsed(false)`.

4. **`ClientViewToggle.tsx` not yet deleted** — The old toggle component is deprecated but retained because existing test files reference it. Delete after the test suite is updated.
