---
title: "Phase 2: App Shell and Sidebar Navigation"
status: pending
version: "1.0"
phase: 2
---

# Phase 2: App Shell and Sidebar Navigation

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Building Block View — Components diagram]`
- `[ref: SDD/Building Block View — Directory Map; src/components/Layout/]`
- `[ref: SDD/Implementation Examples — Sidebar width collapse via Flexbox]`
- `[ref: SDD/Implementation Examples — Active nav item with left accent bar]`
- `[ref: SDD/Cross-Cutting Concepts — UI Visualization Guide — Sidebar Wireframe]`
- `[ref: SDD/Runtime View — Complex Logic: GetVisibleNavLinks]`
- `[ref: SDD/ADR-2 — Flexbox app shell]`
- `[ref: PRD/Feature 1 — Collapsible Sidebar Navigation; Acceptance Criteria]`

**Key Decisions**:
- ADR-2: `flex h-screen` shell; sidebar uses `transition-[width] duration-300 ease-in-out` between `w-60` and `w-16` — NOT `transition-all`
- Active nav item: `before:absolute before:left-0 before:top-0 before:bottom-0 before:w-0.5 before:bg-blue-500` + `bg-gray-800 text-white`
- Sidebar footer: advisor name from `useAuthStore` (fallback: "Advisor"); DataFreshness moved here from DashboardPage top bar
- System Health (`/admin`) nav entry: below separator, dimmer text (`text-gray-500`), hidden in client view

**Dependencies**:
- Phase 1 complete (shadcn/ui `cn()`, `Separator`, uiStore `isSidebarCollapsed`)

---

## Tasks

Replaces the flat top navbar with a collapsible dark sidebar. All authenticated pages render inside `AppShell`. The `App.tsx` route definitions are updated to wrap pages in `AppShell`.

- [ ] **T2.1 AppShell layout component** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/App.tsx` to understand current `AppNav` + page structure `[ref: SDD/Implementation Boundaries — Can Modify: App.tsx]`
  2. Test: Write `src/tests/AppShell.test.tsx`: renders sidebar + main content slot; applies `w-60` when `isSidebarCollapsed=false`; applies `w-16` when `isSidebarCollapsed=true`; children render in main slot
  3. Implement: Create `src/components/Layout/AppShell.tsx`:
     - `flex h-screen overflow-hidden bg-gray-50` outer wrapper
     - Sidebar slot: `bg-gray-900 flex flex-col shrink-0 transition-[width] duration-300 ease-in-out` with conditional `w-60` / `w-16`
     - Main slot: `flex-1 overflow-auto` div containing `{children}`
     - Reads `isSidebarCollapsed` from uiStore
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] Sidebar animates width with `transition-[width]` (not `transition-all`) `[ref: SDD/ADR-2; SDD/Gotchas]`
     - [ ] Main content fills remaining width via `flex-1` `[ref: SDD/Implementation Examples — AppShell]`

- [ ] **T2.2 Sidebar navigation with collapse toggle** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/App.tsx` NAV_LINKS; read SDD Runtime View GetVisibleNavLinks algorithm `[ref: SDD/Runtime View — Complex Logic]`
  2. Test: Write `src/tests/Sidebar.test.tsx`: shows expanded labels when `isSidebarCollapsed=false`; hides labels when `isSidebarCollapsed=true`; active route shows left accent bar + `text-white`; non-active shows `text-gray-400`; collapse toggle calls `toggleSidebar()`; client view hides Goal Planner, Risk Profiler, Scenarios, System Health nav items
  3. Implement: Create `src/components/Layout/Sidebar.tsx` and `src/components/Layout/SidebarNav.tsx`:
     - Nav items use `NavLink` with `isActive` callback; active: `before:absolute before:left-0 before:top-0 before:bottom-0 before:w-0.5 before:bg-blue-500 bg-gray-800 text-white`; inactive: `text-gray-400 hover:text-gray-100 hover:bg-gray-800`
     - Labels hidden when collapsed: `{!isSidebarCollapsed && <span>{label}</span>}`
     - Radix `Tooltip` wraps each nav item when collapsed (shows label on hover)
     - Collapse toggle button calls `toggleSidebar()` from uiStore
     - `GetVisibleNavLinks` logic: if `isClientView` return Dashboard only; else return all 4 + System Health (below separator, `text-gray-500`)
     - Use `Separator` from `src/components/ui/separator.tsx` between main nav and System Health
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] Active item shows left blue accent bar `[ref: PRD/AC Feature 1; SDD/Implementation Examples]`
     - [ ] Collapsed state shows icons + Tooltip labels only `[ref: PRD/AC Feature 1 — tooltip on hover]`
     - [ ] Client view shows Dashboard nav item only `[ref: PRD/AC Feature 2 — nav items in client view]`
     - [ ] System Health appears below separator with dimmer treatment `[ref: PRD/Feature 1 AC; SDD/Wireframe]`

- [ ] **T2.3 Sidebar footer with advisor info and DataFreshness** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/store/authStore.ts` for advisor shape; read `frontend/src/components/Dashboard/DataFreshness.tsx` `[ref: SDD/Integration Points — SidebarFooter → authStore]`
  2. Test: Write test in `src/tests/SidebarFooter.test.tsx`: renders advisor name from authStore; renders "Advisor" fallback when name is null; renders DataFreshness component; Sign out button calls `logout()` and navigates to `/login`
  3. Implement: Create `src/components/Layout/SidebarFooter.tsx`:
     - Read `advisor.name` and `advisor.email` from `useAuthStore`; fallback to "Advisor" if null
     - Render `DataFreshnessBar` component (reads `dataFreshness` from dashboardStore directly — remove prop passing)
     - Sign out button calls `logout()` + `navigate('/login')`
     - Show text only when `!isSidebarCollapsed`; show icon-only when collapsed
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] Advisor name from authStore (fallback "Advisor") `[ref: PRD/Open Questions resolved; SDD/Error Handling]`
     - [ ] DataFreshness visible in sidebar footer `[ref: PRD/Feature 1 AC — DataFreshness in sidebar footer]`
     - [ ] Sign out functional `[ref: SDD/Implementation Boundaries — Must Preserve: existing auth flow]`

- [ ] **T2.4 App.tsx refactor — integrate AppShell, remove AppNav** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/App.tsx` fully; note all pages that currently use `<AppNav>` `[ref: SDD/Implementation Boundaries — Can Modify: App.tsx, AppNav]`
  2. Test: Update `src/tests/` integration smoke: app loads, sidebar visible, AppNav NOT present in DOM, all routes still accessible
  3. Implement: Refactor `App.tsx`:
     - Replace `AppNav` + per-page nav with `AppShell` wrapping all `ProtectedRoute` pages
     - `DashboardPage`, `GoalsPage`, `RiskProfilerPage`, `ScenariosPage`, `AdminPage` all render inside `AppShell`
     - Remove `<AppNav>` from each page component; pages become content-only
     - `LoginForm` page remains outside `AppShell` (no auth)
     - `DataFreshnessBar` removed from `DashboardPage` top bar (now in `SidebarFooter`)
  4. Validate: `npm run dev` — navigate all routes, sidebar persists; `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] All 5 routes (`/dashboard`, `/goals`, `/risk-profiler`, `/scenarios`, `/admin`) render inside AppShell with sidebar `[ref: SDD/Building Block View]`
     - [ ] `/login` renders without AppShell `[ref: SDD/Implementation Boundaries]`
     - [ ] No `AppNav` component rendered anywhere `[ref: SDD/Building Block View — AppNav removed]`
     - [ ] Sidebar collapse state persists across route changes `[ref: PRD/AC Feature 1 — sidebar state]`

- [ ] **T2.5 Phase 2 Validation** `[activity: validate]`

  - Run `npm test -- --run`. Run `npm run typecheck`. Run `npm run build`.
  - Manual smoke: navigate to `/dashboard`, collapse sidebar, navigate to `/goals` — sidebar stays collapsed.
  - Verify sidebar shows left accent on active route, icons + tooltip when collapsed.
  - Check that `isClientView=true` hides Goal Planner, Risk Profiler, Scenarios from sidebar.
