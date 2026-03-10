---
title: "Phase 1: Foundation — uiStore, Dark Class, Layout"
status: completed
version: "1.0"
phase: 1
---

# Phase 1: Foundation — uiStore, Dark Class, Layout

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Architecture Decisions — ADR-1, ADR-5]`
- `[ref: SDD/Implementation Examples 1, 2, 3, 4]`
- `[ref: SDD/Data Models — UIState NEW FIELDS]`
- `[ref: SDD/Acceptance Criteria — Theme Toggle, Preserved Behavior]`

**Key Decisions**:
- ADR-1: `document.documentElement.classList.toggle('dark', isDarkMode)` in a root `useEffect` in `App()` function
- ADR-5: `isDarkMode` initializes from `localStorage.getItem('theme') !== 'light'` — defaults to `true` (dark)
- uiStore must be additive only — all 7 existing fields preserved

**Dependencies**:
- None — this is the foundation phase

---

## Tasks

Establishes the dark mode infrastructure: store state, DOM class application, layout cleanup, and the theme toggle button. All subsequent token migrations depend on this phase being complete.

- [ ] **T1.1 uiStore extension with isDarkMode + toggleTheme** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/store/uiStore.ts` fully to understand existing shape (isSidebarCollapsed, toggleSidebar, setSidebarCollapsed, isClientView, setClientView, selectedProduct, setSelectedProduct) `[ref: SDD/Data Models — UIState MODIFIED]`
  2. Test: Write/extend `src/tests/uiStore.test.ts`:
     - `isDarkMode` defaults to `true` when localStorage has no 'theme' key
     - `isDarkMode` defaults to `true` when localStorage has 'theme' = 'dark'
     - `isDarkMode` defaults to `false` when localStorage has 'theme' = 'light'
     - `toggleTheme()` flips isDarkMode from true to false
     - `toggleTheme()` writes 'light' to localStorage when switching to light
     - `toggleTheme()` writes 'dark' to localStorage when switching to dark
     - All existing sidebar + clientView store behaviors unchanged
  3. Implement: Add to `src/store/uiStore.ts` (additive only):
     - `isDarkMode: boolean` — init: `typeof window !== 'undefined' ? localStorage.getItem('theme') !== 'light' : true`
     - `toggleTheme: () => void` — flip + write localStorage `[ref: SDD/Example 1]`
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] `isDarkMode` defaults to true (dark) on first visit `[ref: SDD/AC — Theme Toggle]`
     - [ ] `toggleTheme()` updates store + localStorage `[ref: SDD/AC — Theme Toggle]`
     - [ ] All existing uiStore tests still pass `[ref: SDD/AC — Preserved Behavior]`

- [ ] **T1.2 App.tsx root dark class useEffect + page layout cleanup** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/App.tsx` fully; note all page container `max-w-*` classes and the DashboardPage filter bar `bg-white` `[ref: SDD/Example 2]`
  2. Test: Write `src/tests/DarkMode.test.tsx`:
     - When `isDarkMode=true`: `document.documentElement.classList.contains('dark')` is true
     - When `isDarkMode=false`: `document.documentElement.classList.contains('dark')` is false
     - DashboardPage filter bar renders with `bg-card` class (not `bg-white`)
     - GoalsPage main has no `max-w-4xl` class
  3. Implement: In `App.tsx`:
     - Add `const isDarkMode = useUIStore((s) => s.isDarkMode)` in `App()` function
     - Add `useEffect(() => { document.documentElement.classList.toggle('dark', isDarkMode) }, [isDarkMode])`
     - In `DashboardPage`: change filter bar header div from `bg-white` to `bg-card`; inner `<main>`: remove `max-w-7xl mx-auto`, change `py-6` to `py-4`
     - In `GoalsPage`: remove `max-w-4xl mx-auto`, change `py-6` to `py-4`
     - In `RiskProfilerPage`: remove `max-w-4xl mx-auto`, change `py-6` to `py-4`
     - In `ScenariosPage`: remove `max-w-5xl mx-auto`, change `py-6` to `py-4`
     - In `AdminPage`: remove `max-w-7xl mx-auto`, change `py-6` to `py-4`; change empty state `text-gray-400` to `text-muted-foreground` `[ref: SDD/Technical Debt]`
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] `dark` class applied to `<html>` when `isDarkMode=true` `[ref: SDD/AC — Content Area Appearance]`
     - [ ] All page containers fill full content area width `[ref: SDD/AC — GoalForm Layout]`

- [ ] **T1.3 AppShell background token + SidebarFooter theme toggle button** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Layout/AppShell.tsx` and `frontend/src/components/Layout/SidebarFooter.tsx` fully `[ref: SDD/Example 3, 4; SDD/Building Block View — AppShell, SidebarFooter]`
  2. Test: Write/extend `src/tests/SidebarFooter.test.tsx`:
     - Renders Moon icon when `isDarkMode=true`
     - Renders Sun icon when `isDarkMode=false`
     - Button has `aria-label="Switch to light mode"` when dark
     - Button has `aria-label="Switch to dark mode"` when light
     - Clicking button calls `toggleTheme()`
     - Icon-only (no label text) when `isSidebarCollapsed=true`
     - Label visible when `isSidebarCollapsed=false`
  3. Implement:
     - In `AppShell.tsx`: change outer div from `bg-gray-50` to `bg-background`; add `border-r border-border` to `<aside>` element `[ref: SDD/Gotchas — dark sidebar/content boundary]`
     - In `SidebarFooter.tsx`: add `isDarkMode` and `toggleTheme` from `useUIStore`; add Moon/Sun toggle button with `aria-label` following collapsed/expanded pattern `[ref: SDD/Example 4]`
     - Import `Moon` and `Sun` from `lucide-react`
  4. Validate: `npm run test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] AppShell outer bg uses `bg-background` token `[ref: SDD/Example 3]`
     - [ ] Theme toggle button renders correctly in both collapsed/expanded states `[ref: SDD/AC — Theme Toggle]`
     - [ ] Sidebar/content area boundary visible in dark mode `[ref: SDD/Gotchas 5]`

- [ ] **T1.4 Phase 1 Validation** `[activity: validate]`

  - Run `npm run test -- --run`. Run `npm run typecheck`. Run `npm run build`.
  - Toggle isDarkMode in test — verify `dark` class on `document.documentElement`.
  - Verify uiStore preserves all existing fields.
  - Check sidebar theme button renders in both sidebar states.
