---
title: "Phase 1: Foundation — shadcn/ui, Inter Font, uiStore"
status: pending
version: "1.0"
phase: 1
---

# Phase 1: Foundation — shadcn/ui, Inter Font, uiStore

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Constraints; CON-1 through CON-7]`
- `[ref: SDD/Implementation Context — Project Commands]`
- `[ref: SDD/Building Block View — Directory Map; src/lib/, src/index.css, tailwind.config.ts]`
- `[ref: SDD/ADR-1 — shadcn/ui coexistence token strategy]`
- `[ref: SDD/ADR-3 — uiStore isSidebarCollapsed]`
- `[ref: SDD/Cross-Cutting Concepts — Design System tokens]`

**Key Decisions**:
- ADR-1: Coexistence strategy — run `npx shadcn@latest init`, override `--primary` to HSL `219 90% 56%` (blue-600), keep existing Tailwind color classes untouched
- ADR-3: Add `isSidebarCollapsed: boolean`, `toggleSidebar()`, `setSidebarCollapsed(v)` to uiStore; read/write localStorage key `sidebar_collapsed` on init and change
- Inter font: `@fontsource/inter` weights 400, 500, 600; set `fontFamily.sans` in tailwind config

**Dependencies**:
- None — this is the foundation phase

---

## Tasks

Establishes the technical foundation: shadcn/ui component library, Inter font, CSS variable tokens, and extended uiStore. All subsequent phases depend on these deliverables.

- [ ] **T1.1 shadcn/ui initialization and component installation** `[activity: frontend-ui]`

  1. Prime: Read `frontend/tailwind.config.ts`, `frontend/src/index.css`, `frontend/package.json` to understand current setup `[ref: SDD/Implementation Context — Code Context]`
  2. Test: Verify `src/components/ui/` does not exist yet; verify `src/lib/utils.ts` does not exist
  3. Implement:
     - Run `npx shadcn@latest init` (style: New York, base color: Slate, CSS variables: yes)
     - Run `npx shadcn@latest add button input card badge select skeleton tooltip separator`
     - Override `--primary` in `src/index.css` `:root` block to `219 90% 56%` (blue-600)
     - Verify `components.json` created at project root
  4. Validate: `npm run typecheck` passes; `npm run build` succeeds; `src/components/ui/` contains 8 component files; `src/lib/utils.ts` exports `cn()`
  5. Success:
     - [ ] `src/components/ui/button.tsx`, `input.tsx`, `card.tsx`, `badge.tsx`, `select.tsx`, `skeleton.tsx`, `tooltip.tsx`, `separator.tsx` all exist `[ref: SDD/Directory Map]`
     - [ ] `src/lib/utils.ts` exports `cn()` combining clsx + tailwind-merge `[ref: SDD/Gotchas — cn() import]`
     - [ ] `--primary` CSS variable = `219 90% 56%` in `src/index.css` `[ref: SDD/ADR-1]`

- [ ] **T1.2 Inter font setup** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/index.css` and `frontend/tailwind.config.ts` `[ref: SDD/Cross-Cutting Concepts — Design System]`
  2. Test: Verify Inter is not currently loaded; current font is system-ui
  3. Implement:
     - Run `npm install @fontsource/inter`
     - Add to top of `src/index.css`: `@import '@fontsource/inter/400.css'`, `@import '@fontsource/inter/500.css'`, `@import '@fontsource/inter/600.css'` (before `@tailwind` directives)
     - Add to `tailwind.config.ts` `theme.extend`: `fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] }`
  4. Validate: `npm run build` succeeds; browser DevTools computed style shows `font-family: Inter` on body
  5. Success:
     - [ ] `@fontsource/inter` in `package.json` dependencies `[ref: SDD/Cross-Cutting Concepts]`
     - [ ] `tailwind.config.ts` sets `fontFamily.sans` to Inter `[ref: SDD/Quality Requirements — Inter font]`
     - [ ] Three weight imports (400, 500, 600) in `index.css` `[ref: SDD/Cross-Cutting Concepts]`

- [ ] **T1.3 uiStore extension with sidebar collapse state** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/store/uiStore.ts` fully to understand current shape `[ref: SDD/Application Data Models — uiStore extension]`
  2. Test: Write test in `src/tests/uiStore.test.ts` (or extend existing): `isSidebarCollapsed` defaults to false; `toggleSidebar()` flips it; `setSidebarCollapsed(true)` sets to true; localStorage key `sidebar_collapsed` is read on init and written on change
  3. Implement: Add to `uiStore.ts`:
     - `isSidebarCollapsed: boolean` (init: read `localStorage.getItem('sidebar_collapsed') === 'true'`, default false)
     - `toggleSidebar: () => void` (flip + write localStorage)
     - `setSidebarCollapsed: (v: boolean) => void` (set + write localStorage)
  4. Validate: `npm test -- --run` passes; `npm run typecheck` clean
  5. Success:
     - [ ] `isSidebarCollapsed` initializes from localStorage `[ref: SDD/ADR-3; PRD/AC sidebar persistence]`
     - [ ] `toggleSidebar()` and `setSidebarCollapsed()` update both store and localStorage `[ref: SDD/ADR-3]`
     - [ ] Existing `isClientView`, `setClientView`, `selectedProduct`, `setSelectedProduct` remain unchanged `[ref: SDD/Implementation Boundaries — Must Preserve]`

- [ ] **T1.4 Phase 1 Validation** `[activity: validate]`

  - Run `npm test -- --run`. Run `npm run typecheck`. Run `npm run build`.
  - Verify all T1.1–T1.3 success criteria met.
  - Check `src/components/ui/` has 8 files, `src/lib/utils.ts` exists, Inter imports in `index.css`, uiStore has new fields.
