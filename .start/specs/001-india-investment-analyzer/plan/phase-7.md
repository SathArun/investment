---
title: "Phase 7: React Dashboard & Core UI"
status: completed
version: "1.0"
phase: 7
---

# Phase 7: React Dashboard & Core UI

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/User Interface & UX; Information Architecture, Design System, ASCII Wireframe]`
- `[ref: SDD/User Interface & UX; Screen Flow diagram]`
- `[ref: SDD/Runtime View; Primary Flow; sequence diagram]`
- `[ref: PRD/Feature 1 Multi-Asset Dashboard AC]` — Dashboard acceptance criteria
- `[ref: PRD/Feature 2 Composite Advisor Score AC]` — Score breakdown panel
- `[ref: PRD/Feature 3 Tax Overlay Engine AC]` — Tax bracket banner
- `[ref: PRD/Feature 4 Client Presentation Mode AC]` — Client view mode

**Key Decisions**:
- ADR-7: React 18 + Zustand + Recharts + Shadcn/ui + Tailwind
- Filter changes re-sort from Zustand cache (instant); tax bracket change triggers new API call
- Client View is a React context that suppresses advisor-only components (Sharpe, sub-scores)
- Risk labels map: SEBI level 1-6 → plain language strings in `src/utils/riskLabel.ts`

**Dependencies**:
- Phase 1 complete (frontend scaffold)
- Phase 4 complete (`GET /api/products` API working with real scores)
- Phase 5 complete (auth API for login)

---

## Tasks

Builds the full React dashboard: login, multi-asset table with scoring, tax overlay, score breakdown, risk-return scatter plot, client view mode, and PDF/WhatsApp trigger.

- [x] **T7.1 Login screen + auth state management** `[activity: frontend-ui]`

  1. Prime: Read `[ref: SDD/Internal API Changes; POST /api/auth/login]` and `[ref: SDD/System-Wide Patterns; Security; Axios interceptor]`
  2. Test (Vitest + React Testing Library): Login form renders email + password fields + submit button; submitting with valid credentials calls `POST /api/auth/login` and stores `access_token` in Zustand store; invalid credentials shows error message "Invalid email or password"; authenticated routes redirect to dashboard; unauthenticated user accessing `/dashboard` redirects to `/login`; Axios interceptor attaches `Authorization: Bearer {token}` to all requests
  3. Implement: Create `src/api/client.ts` (Axios instance; request interceptor adds JWT; response interceptor handles 401 → auto-refresh); `src/store/authStore.ts` (Zustand: `advisor`, `accessToken`, `login()`, `logout()`); `src/components/Login/LoginForm.tsx`; `src/App.tsx` with React Router routes (`/login`, `/dashboard`, `/goals`, `/risk-profiler`, `/scenarios`); protected route wrapper
  4. Validate: Playwright/Vitest: login with test credentials → lands on dashboard; refresh page → stays logged in (token in localStorage); logout → redirects to login; 401 response → auto-refreshes token and retries once
  5. Success:
    - [x]Advisor remains logged in across page refresh (JWT in localStorage) `[ref: SDD/Runtime View]`
    - [x]401 triggers token refresh + automatic retry before showing login screen `[ref: SDD/Error Handling; JWT expired]`

- [x] **T7.2 Filter bar + Zustand filter store** `[activity: frontend-ui]`

  1. Prime: Read `[ref: SDD/User Interface & UX; ASCII Wireframe; FilterBar row]` and `[ref: SDD/User Interface & UX; Interaction Design; Filter changes]`
  2. Test: Filter bar renders Tax Bracket selector (5 options: 0%, 5%, 10%, 20%, 30%), Time Horizon selector (3 options), Risk Filter selector (All, Conservative, Moderate, Aggressive); changing Tax Bracket dispatches `setTaxBracket(0.30)` to Zustand store AND triggers new `GET /api/products` call; changing sort column (by clicking table header) updates store without API call; tax bracket banner "Post-tax returns shown — FY2025-26 tax rules" visible when any non-zero bracket selected `[ref: PRD/Feature 3 AC; banner]`
  3. Implement: Create `src/store/filterStore.ts` (Zustand: `taxBracket`, `timeHorizon`, `riskFilter`, `sortBy`, `sortDir`, setters); `src/components/Dashboard/FilterBar.tsx` with Shadcn/ui Select dropdowns; `src/store/dashboardStore.ts` (Zustand: `products[]`, `dataFreshness`, `isLoading`, `fetchProducts()`); react-query or useEffect on filter changes to re-fetch when bracket/horizon changes
  4. Validate: RTL tests: bracket change → API called with new bracket; sort change → API NOT called (re-sorts cached products in store); banner appears/disappears correctly; `data_freshness` timestamps rendered in `DataFreshness` component
  5. Success:
    - [x]Changing time horizon or risk filter re-ranks table from cached scores without API call `[ref: SDD/User Interface & UX; Interaction Design; Filter changes]`
    - [x]Changing tax bracket triggers new API call and updates post-tax return column `[ref: PRD/Feature 3 AC]`
    - [x]Tax bracket banner visible when bracket > 0% `[ref: PRD/Feature 3 AC; banner]`

- [x] **T7.3 Multi-asset ranking table** `[activity: frontend-ui]`

  1. Prime: Read `[ref: SDD/User Interface & UX; ASCII Wireframe]` and `[ref: PRD/Feature 1 AC; sortable table, tooltip, ≥ 12 asset class categories]`
  2. Test: Table renders all products from store; clicking "3Y CAGR" header sorts ascending, second click sorts descending, sort column highlighted; hovering a row opens tooltip with: 1Y/3Y/5Y/10Y returns, std_dev, max_drawdown, expense_ratio, min_investment, SEBI risk label, liquidity rating `[ref: PRD/Feature 1 AC; hover tooltip]`; products with N/A data show "—" not "0" or "null"; clicking pin icon adds product to `pinnedProducts` store; SEBI risk level renders as colored dots (1=green, 6=red) matching riskLabel map
  3. Implement: Create `src/components/Dashboard/AssetTable.tsx` with sortable columns (click header → update `filterStore.sortBy/sortDir`); cells for: pin checkbox, product name, SEBI risk dots, 1Y/3Y/5Y CAGR, post-tax return, Advisor Score; hover Tooltip (Shadcn Tooltip component) with full metrics; `src/utils/riskLabel.ts` mapping 1-6 → plain English; null/undefined values render as "—"
  4. Validate: RTL tests: 12+ asset class rows rendered; sort on CAGR works; tooltip shows all 10 required fields; pin adds to `pinnedProducts`; N/A data renders "—"; crypto row shows disclaimer badge
  5. Success:
    - [x]Table shows ≥ 12 asset class categories `[ref: PRD/Feature 1 AC]`
    - [x]Sort reorders instantly (< 1 second, no API call) `[ref: PRD/Feature 1 AC; sort instantly]`
    - [x]Hover tooltip shows all 10 required fields `[ref: PRD/Feature 1 AC; tooltip]`

- [x] **T7.4 Score breakdown side panel** `[activity: frontend-ui]`

  1. Prime: Read `[ref: PRD/Feature 2 AC; score breakdown panel]` — 6 sub-scores with plain-language descriptions
  2. Test: Clicking "Score Breakdown" on a product opens a slide-in panel showing 6 labeled bar segments; each bar has a plain-language label (e.g., "High Liquidity — exit within 1 business day", "Low Expense — minimal fees reduce drag"); closing panel with Escape key works; panel stays open while user scrolls the table; two products can't both have breakdown open simultaneously
  3. Implement: Create `src/components/Dashboard/ScoreBreakdown.tsx` as a fixed right-side panel (Shadcn Sheet component); renders 6 sub-scores as horizontal bars (Shadcn Progress or custom); maps sub-score names to plain-language descriptions per `src/utils/riskLabel.ts`; triggered by button click on each table row; `selectedProduct` in Zustand store controls visibility
  4. Validate: RTL: click breakdown button → panel opens with all 6 scores; Escape closes; plain-language labels present for all 6 sub-scores; sub-scores sum to weighted composite (verify in test)
  5. Success:
    - [x]Score breakdown panel shows all 6 sub-scores with plain-language descriptions `[ref: PRD/Feature 2 AC; breakdown panel]`
    - [x]Panel does not block table interaction while open `[ref: SDD/User Interface & UX; Score Breakdown panel]`

- [x] **T7.5 Risk-return scatter plot** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `[ref: SDD/User Interface & UX]` — Recharts scatter; X = std_dev, Y = post_tax_return, bubble size = AUM proxy, color = asset class category
  2. Test: ScatterChart renders with products from store; X-axis labeled "Risk (Std Dev)"; Y-axis labeled "Post-Tax Return (3Y)"; hovering a bubble shows product name and key metrics; products with null std_dev are excluded from scatter (not shown as 0); color coding matches category (blue = Equity, green = Debt, gold = Gold, grey = Fixed)
  3. Implement: Create `src/components/Dashboard/RiskReturnPlot.tsx` using Recharts `ScatterChart`; map `products` from store filtering out null std_dev; custom `<Tooltip>` content component; color map by asset category; responsive container
  4. Validate: RTL: chart renders with ≥ 5 data points; tooltip visible on hover; null std_dev products not plotted; category colors match spec
  5. Success: Risk-return scatter plot renders all products with non-null std_dev, colored by asset class `[ref: SDD/User Interface & UX; Risk-Return Scatter]`

- [x] **T7.6 Client View mode + PDF trigger + WhatsApp share** `[activity: frontend-ui]`

  1. Prime: Read `[ref: PRD/Feature 4 AC]` — all 4 acceptance criteria for Client Presentation Mode
  2. Test: Clicking "Client View" toggle switches `isClientView` in Zustand; in client view: Sharpe ratio column hidden, std_dev hidden, score breakdown button hidden; risk column shows plain-language labels ("LOW — Your principal is very safe") not numbers; "Generate PDF" button enabled when ≥ 1 and ≤ 5 products pinned; clicking "Generate PDF" calls `POST /api/pdf/client-report` and opens PDF in new tab; "Share via WhatsApp" button on PDF preview opens `https://wa.me/?text=...` in new tab
  3. Implement: Create `src/components/Presentation/ClientView.tsx` context; `src/components/Presentation/ShareWhatsApp.tsx` with `wa.me` URL builder; update `AssetTable.tsx` to conditionally hide advisor-only columns when `isClientView`; "Generate PDF" button in `src/components/Presentation/ProductPins.tsx` calling PDF API; loading spinner during PDF generation; error toast if generation fails
  4. Validate: RTL: client view hides correct columns; PDF API called on button click; WhatsApp URL contains correct PDF link; 6-product selection shows validation error "Max 5 products"; 0-product selection disables button
  5. Success:
    - [x]Client view hides Sharpe ratios and numerical sub-scores `[ref: PRD/Feature 4 AC]`
    - [x]"Share via WhatsApp" opens wa.me with PDF link `[ref: SDD/ADR-5; WhatsApp deep link]`
    - [x]PDF generation blocked when > 5 products selected `[ref: SDD/Internal API Changes; POST /api/pdf/client-report; product_ids max 5]`

- [x] **T7.7 Phase 7 Validation** `[activity: validate]`

  - Run `npm run typecheck` and `npm run lint`. Run Vitest test suite. Open dev server and manually test: login → dashboard → filter → sort → hover tooltip → score breakdown → client view → PDF generation → WhatsApp share. Assert full workflow completes without console errors.

---

**Phase 7 Exit Criteria**: Full dashboard working end-to-end; all PRD Feature 1-4 acceptance criteria met; client view hides advisor metrics; PDF generates; WhatsApp share opens correctly; all frontend tests pass.
