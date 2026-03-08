---
title: "Phase 4: ProductPins Hero Cards and Skeleton Loaders"
status: pending
version: "1.0"
phase: 4
---

# Phase 4: ProductPins Hero Cards and Skeleton Loaders

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Application Data Models — ProductPinCard props interface]`
- `[ref: SDD/Building Block View — Directory Map; ProductPinCard.tsx, ViewToggle.tsx]`
- `[ref: SDD/Cross-Cutting Concepts — User Interface; hero card layout]`
- `[ref: PRD/Feature 3 — ProductPins Hero Card Layout; Acceptance Criteria]`
- `[ref: PRD/Feature 4 — Skeleton Loading States; Acceptance Criteria]`
- `[ref: SDD/Acceptance Criteria — Skeleton Loaders (CLS=0, prefers-reduced-motion)]`

**Key Decisions**:
- ProductPinCard: responsive grid `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`; per-card: name (lg semibold, 2-line clamp), asset class badge (gray), SEBI risk badge (color-coded), post-tax 3Y return (2xl bold blue-600), 5Y CAGR (sm gray)
- Skeleton heights must match final content heights exactly to achieve CLS=0
- `prefers-reduced-motion`: skeleton `animate-pulse` disabled via `motion-reduce:animate-none`
- Use shadcn/ui `Skeleton` component from Phase 1 for all loading states
- Use shadcn/ui `Badge` for risk level and asset class badges in ProductPinCard

**Dependencies**:
- Phase 1 complete (shadcn/ui `Skeleton`, `Badge`, `Card`)
- Phase 3 complete (`isClientView` wiring in DashboardPage, ProductPins conditional rendering)

---

## Tasks

Redesigns the ProductPins section as a hero card grid in client view, and adds professional skeleton loading states to replace all "Loading..." text placeholders.

- [ ] **T4.1 ProductPinCard component** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Presentation/ProductPins.tsx` to understand current data shape and pin management; read SDD ProductPinCard props interface `[ref: SDD/Application Data Models — ProductPinCard]`
  2. Test: Write `src/tests/ProductPinCard.test.tsx`: renders product name; renders asset class Badge; renders SEBI risk Badge with correct color (1-2=green, 3=yellow, 4=orange, 5-6=red); renders post-tax 3Y return in blue; renders 5Y CAGR if available; truncates long name with tooltip; unpin button calls onUnpin with product id
  3. Implement: Create `src/components/Presentation/ProductPinCard.tsx`:
     - Use shadcn/ui `Card`, `CardContent`, `Badge` from `src/components/ui/`
     - Product name: `text-lg font-semibold line-clamp-2`; full name in Radix `Tooltip` on hover
     - Asset class: `<Badge variant="secondary">{asset_class}</Badge>`
     - SEBI risk badge color logic: `sebi_risk_level <= 2` → green, `=3` → yellow, `=4` → orange, `>=5` → red
     - Post-tax 3Y: `text-2xl font-bold text-blue-600`
     - 5Y CAGR: `{cagr_5y !== null && <span className="text-sm text-gray-500">{formatPct(cagr_5y)} 5Y</span>}`
     - Unpin: star icon button bottom-right, `onClick={() => onUnpin(product.id)}`
     - Hover: `hover:shadow-md transition-shadow duration-200`
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] All 5 data fields rendered per card (name, asset class, risk, post-tax return, 5Y) `[ref: PRD/AC Feature 3; SDD/ProductPinCard props]`
     - [ ] SEBI risk badge color-coded correctly `[ref: PRD/Feature 3 — card layout]`
     - [ ] Long name truncated with tooltip `[ref: SDD/Edge Cases — long product names]`

- [ ] **T4.2 ProductPins hero grid layout in client view** `[activity: frontend-ui]`

  1. Prime: Read `frontend/src/components/Presentation/ProductPins.tsx` fully; identify pinned product data structure and how PDF/WhatsApp buttons are rendered `[ref: SDD/Building Block View — ProductPins.tsx MODIFY]`
  2. Test: Update `src/tests/ProductPins.test.tsx`: in client view with pinned products renders `ProductPinCard` components in grid; in client view with NO pinned products renders empty state "Pin products in Advisor View to build your comparison"; PDF and WhatsApp buttons visible below cards in client view; non-client-view renders existing list layout (no regression)
  3. Implement: Modify `src/components/Presentation/ProductPins.tsx`:
     - When `isClientView=true` AND products pinned: render `<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">` with `<ProductPinCard>` per product
     - When `isClientView=true` AND no products: render empty state `<p>Pin products in Advisor View to build your comparison</p>`
     - PDF generate + WhatsApp share buttons remain below card grid in client view
     - When `isClientView=false`: render existing list layout unchanged
  4. Validate: `npm test -- --run`; `npm run typecheck`; manual: pin 3 products, switch to client view → hero grid
  5. Success:
     - [ ] Hero card grid in client view with pinned products `[ref: PRD/AC Feature 3]`
     - [ ] Empty state message when no pinned products `[ref: PRD/AC Feature 3 — empty state]`
     - [ ] PDF + WhatsApp buttons visible below grid `[ref: PRD/AC Feature 3 — PDF/share visible]`
     - [ ] Advisor view list layout unchanged (no regression) `[ref: SDD/Implementation Boundaries]`

- [ ] **T4.3 AssetTable skeleton loader** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/Dashboard/AssetTable.tsx` loading state; check actual rendered table row height to match skeleton height `[ref: PRD/AC Feature 4 — 5 skeleton rows; SDD/Gotchas — skeleton height CLS]`
  2. Test: Update `src/tests/AssetTable.test.tsx`: when `isLoading=true` and `products=[]`, renders 5 `Skeleton` rows; when `isLoading=false`, renders data rows; no layout shift between states
  3. Implement: In `AssetTable.tsx`:
     - When `isLoading=true` and products empty: render 5 rows of `<Skeleton className="h-[52px] w-full" />` (height must match actual row height — measure first)
     - Import `Skeleton` from `src/components/ui/skeleton`
     - Replace any `"Loading..."` text state with skeleton rows
     - Add `motion-reduce:animate-none` to each Skeleton for reduced-motion accessibility
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] 5 skeleton rows matching column structure during load `[ref: PRD/AC Feature 4]`
     - [ ] CLS=0 — skeleton height equals actual row height `[ref: SDD/Quality Requirements]`
     - [ ] `motion-reduce:animate-none` on skeleton `[ref: PRD/AC Feature 4 — prefers-reduced-motion]`

- [ ] **T4.4 Admin JobCard skeleton loader** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/Admin/JobCard.tsx` to understand card dimensions and current loading state in `AdminPage` (App.tsx) `[ref: PRD/AC Feature 4 — 6 skeleton cards]`
  2. Test: Update `src/tests/JobCard.test.tsx`: when `isLoading=true` and `jobs=[]`, AdminPage renders 6 skeleton cards matching JobCard dimensions
  3. Implement: In `AdminPage` (App.tsx or extracted page):
     - When `isLoading=true && jobs.length === 0`: render `<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">` with 6 `<Skeleton className="h-[140px] rounded-lg" />` (height = measured JobCard height)
     - Replace existing "Loading job status..." text with skeleton grid
     - Add `motion-reduce:animate-none` to each Skeleton
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] 6 skeleton cards in same grid layout as JobCards during initial load `[ref: PRD/AC Feature 4]`
     - [ ] Skeleton dimensions match JobCard (no CLS when data arrives) `[ref: SDD/Quality Requirements]`

- [ ] **T4.5 GoalForm chart area skeleton** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `frontend/src/components/GoalPlanner/GoalForm.tsx` to find chart rendering and loading state `[ref: PRD/AC Feature 4 — GoalForm chart skeleton]`
  2. Test: When GoalForm is calculating results, chart area shows `Skeleton` placeholder of matching height; when results ready, skeleton replaced by chart
  3. Implement: In `GoalForm.tsx`:
     - Identify the chart container height
     - When chart data pending: render `<Skeleton className="h-[200px] w-full rounded-lg motion-reduce:animate-none" />`
     - Replace any loading spinner or blank space in the chart area
  4. Validate: `npm test -- --run`; `npm run typecheck`
  5. Success:
     - [ ] Chart area shows skeleton while calculating `[ref: PRD/AC Feature 4]`
     - [ ] No layout shift when chart renders over skeleton `[ref: SDD/Quality Requirements — CLS=0]`

- [ ] **T4.6 Phase 4 Validation** `[activity: validate]`

  - Run `npm test -- --run`. Run `npm run typecheck`. Run `npm run build`.
  - Manual: pin 2+ products, switch to Client View → hero cards render. Switch back → list view unchanged.
  - Manual: navigate to `/dashboard` on slow connection (Network tab throttle) → 5 skeleton rows visible during load.
  - Manual: navigate to `/admin` → 6 skeleton cards during initial fetch.
  - Check no "Loading..." text remains anywhere in the app.
