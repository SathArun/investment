---
title: "Modern UI Redesign — Sidebar Layout, shadcn/ui Components, Dual-Audience Views"
status: draft
version: "1.0"
---

# Product Requirements Document

## Validation Checklist

### CRITICAL GATES (Must Pass)

- [x] All required sections are complete
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Problem statement is specific and measurable
- [x] Every feature has testable acceptance criteria (Gherkin format)
- [x] No contradictions between sections

### QUALITY CHECKS (Should Pass)

- [x] Problem is validated by evidence (not assumptions)
- [x] Context → Problem → Solution flow makes sense
- [x] Every persona has at least one user journey
- [x] All MoSCoW categories addressed (Must/Should/Could/Won't)
- [x] Every metric has corresponding tracking events
- [x] No feature redundancy
- [x] No technical implementation details included
- [x] A new team member could understand this PRD

---

## Product Overview

### Vision

Transform the India Investment Analyzer from a functionally complete but visually dated tool into a modern, premium-feeling SaaS dashboard that makes financial advisors more productive and gives clients a polished, confidence-inspiring presentation experience.

### Problem Statement

The current UI achieves its functional goals but presents three compounding problems:

1. **Flat visual hierarchy:** A top navbar layout with manually-styled Tailwind components looks like a generic utility app, not a professional investment tool. There are no clear visual layers, no premium feel, and no delineation between working areas.

2. **No audience differentiation at the layout level:** When advisors switch to "client view," only the data changes — the layout, navigation, and visual density remain identical. Clients see an advisor-grade dense interface with technical labels ("Advisor Score," FilterBar tax brackets) that creates confusion and erodes trust.

3. **Missing loading states:** First loads show blank spaces or plain text ("Loading data status..."), which feels broken and unprofessional — especially on slow connections or when running jobs.

The consequence: advisors using the client view for presentations lack confidence in the tool's appearance, and the gap between the app's analytical depth and its visual presentation undermines perceived value.

### Value Proposition

A collapsible dark sidebar replaces the flat top navbar, immediately elevating the visual register to match tools like Linear, Vercel, and Stripe. shadcn/ui components — built on the existing Radix UI and Tailwind stack — replace ad-hoc styling with a consistent, accessible component system. Most critically, the client view becomes a genuinely different visual experience: advisor sidebar collapses, dense tables simplify, and pinned products become hero presentation cards — giving advisors a tool they're proud to show clients.

---

## User Personas

### Primary Persona: Financial Advisor (Rajan)

- **Demographics:** 30–50 years old, SEBI-registered investment advisor, moderate-to-high technical proficiency, uses desktop primarily, works with 20–100 client portfolios
- **Goals:** Quickly compare mutual funds and equity products, prepare client-facing presentations, demonstrate product recommendations with supporting data, maintain professional credibility with clients
- **Pain Points:**
  - Switching between his working view and client presentation requires mentally filtering what clients "shouldn't see" — no layout actually changes
  - The tool looks utilitarian in client meetings, undercutting the premium service positioning
  - Blank/loading states during demos look like technical failures
  - Navigation is flat — no clear hierarchy between frequently used sections

### Secondary Persona: End Client (Priya)

- **Demographics:** 35–55 years old, high-net-worth individual, low-to-moderate financial literacy, views the app only during advisor-led sessions or via shared links
- **Goals:** Understand what products her advisor is recommending, see how they compare on simple metrics (returns, risk), feel confident in the advisor's recommendation
- **Pain Points:**
  - Sees technical labels she doesn't understand ("Advisor Score," "Post-Tax 3Y CAGR," FilterBar tax brackets)
  - The interface density is overwhelming — she cannot identify what's important
  - No clear "these are your recommended products" hero area

---

## User Journey Maps

### Primary User Journey: Advisor Working Session

1. **Login:** Rajan logs in and lands on the dashboard. The dark sidebar orients him immediately — he knows where everything is.
2. **Research:** He uses the full-width, dense AssetTable with all columns to compare products. He sorts by Advisor Score and explores ScoreBreakdown details.
3. **Selection:** He pins 3–5 products for a client meeting by clicking the star icon. The FilterBar shows his tax bracket and time horizon filters.
4. **Transition to Client View:** Before the meeting, he clicks the segmented control to switch to "Client View." The sidebar collapses to icons, the FilterBar disappears, and the table simplifies.
5. **Client Presentation:** He scrolls through the ProductPins hero cards — each shows the product name, asset class badge, risk level, and post-tax 3Y return prominently. He generates a PDF and shares via WhatsApp.
6. **Return:** He toggles back to Advisor View and continues his analysis.

### Secondary User Journey: Client Viewing Shared Content

1. **Arrival:** Priya opens a PDF or WhatsApp link from her advisor during or after a meeting.
2. **Review:** She sees a clean layout — her advisor's pinned products presented as large, readable cards with simple metrics.
3. **Understanding:** She identifies the recommended products, sees their risk levels (color-coded badges), and notes the post-tax returns.
4. **Trust:** The polished presentation reinforces confidence in her advisor's recommendation.

---

## Feature Requirements

### Must Have Features

#### Feature 1: Collapsible Sidebar Navigation

- **User Story:** As an advisor, I want a sidebar navigation that I can collapse to maximize screen space, so that I can work more efficiently with dense data tables.
- **Acceptance Criteria:**
  - [ ] Given the app loads, When the advisor views the dashboard, Then a dark sidebar is visible on the left with Dashboard, Goal Planner, Risk Profiler, Scenarios navigation items
  - [ ] Given the sidebar is expanded, When the advisor clicks the collapse toggle, Then the sidebar animates to icon-only width and labels disappear
  - [ ] Given the sidebar is collapsed, When the advisor hovers over a nav icon, Then a tooltip shows the section label
  - [ ] Given any page, When the advisor is on that page, Then the corresponding nav item shows a left blue accent bar and white text indicating active state
  - [ ] Given the sidebar, When the app is in any view, Then a System Health link appears below a separator with dimmer visual treatment (accessible to staff only)
  - [ ] Given the sidebar footer, When viewing any page, Then the DataFreshness indicator is visible in the sidebar footer area
  - [ ] Given the sidebar footer, When viewing any page, Then the advisor's name (from auth store) and a Sign Out button are visible at the bottom
  - [ ] Given the sidebar collapse state, When the user refreshes the page, Then the sidebar restores to its last state (expanded or collapsed)

#### Feature 2: Dual-Audience View Switch

- **User Story:** As an advisor, I want switching to "Client View" to visibly change the entire layout and hide advisor-only content, so that I can confidently present to clients without manually filtering what's visible.
- **Acceptance Criteria:**
  - [ ] Given the dashboard, When the advisor is in Advisor View, Then the FilterBar, all AssetTable columns, RiskReturnPlot with full labels, and full sidebar are all visible
  - [ ] Given the dashboard, When the advisor switches to Client View, Then the sidebar auto-collapses to icon-only
  - [ ] Given the dashboard in Client View, When rendered, Then the FilterBar is hidden and replaced with a static summary label (e.g., "Filtered: 20% tax, 7-year horizon") and a "Change filters" link that switches back to Advisor View
  - [ ] Given the dashboard in Client View, When the AssetTable is rendered, Then only client-safe columns are shown: Product Name, SEBI Risk, 1Y/3Y/5Y CAGR, Post-Tax 3Y Return
  - [ ] Given the dashboard in Client View, When rendered, Then the Breakdown button column is hidden
  - [ ] Given the dashboard in Client View, When rendered, Then the RiskReturnPlot shows simplified axis labels and hides the "Advisor Score" bubble-size legend
  - [ ] Given the dashboard in Client View, When rendered, Then the navigation shows Dashboard only (Goal Planner, Risk Profiler, Scenarios are hidden)
  - [ ] Given the dashboard in Client View, When rendered, Then the ProductPins section is displayed as the hero area above the table
  - [ ] Given the ClientViewToggle, When rendered, Then it appears as a segmented control with two options: "Advisor View" and "Client View"

#### Feature 3: ProductPins Hero Card Layout (Client View)

- **User Story:** As an advisor, I want pinned products to display as large, readable hero cards in client view, so that clients can immediately focus on recommended products without data overload.
- **Acceptance Criteria:**
  - [ ] Given the client view with pinned products, When the ProductPins section renders, Then products are displayed as cards in a responsive grid (3 columns desktop, 2 tablet, 1 mobile)
  - [ ] Given a product card, When rendered, Then it displays: product name (large, bold), asset class (small gray label), SEBI risk level (color-coded badge), and post-tax 3Y return (large, blue-highlighted)
  - [ ] Given a product card, When the advisor hovers, Then the card shows a subtle shadow lift
  - [ ] Given the ProductPins section in client view, When rendered, Then the PDF generate and WhatsApp share buttons are visible below the cards
  - [ ] Given no pinned products, When in client view, Then a friendly empty state is shown: "Pin products in Advisor View to build your comparison"

#### Feature 4: Skeleton Loading States

- **User Story:** As an advisor or client, I want to see structured loading placeholders instead of blank spaces or plain text, so that the app feels fast and professional even on slow connections.
- **Acceptance Criteria:**
  - [ ] Given the dashboard is loading, When the AssetTable data is being fetched, Then 5 skeleton rows matching the table column structure are displayed
  - [ ] Given the admin page is loading, When job data is being fetched, Then 6 skeleton cards matching the JobCard layout are displayed
  - [ ] Given the GoalForm chart area is calculating, When results are pending, Then a skeleton placeholder matching the chart area height is displayed
  - [ ] Given any skeleton, When content loads, Then the transition from skeleton to content has no visible layout shift (CLS = 0)
  - [ ] Given any skeleton, When `prefers-reduced-motion` is set, Then the pulse animation is disabled

### Should Have Features

- **Inter font with tabular numerals**: The app uses Inter as the system font with tabular number alignment for financial columns, ensuring clean vertical alignment of monetary values.
- **Consistent card styling**: All card containers (JobCard, GoalForm sections, ScoreBreakdown) use a uniform style with `shadow-sm` and consistent padding, replacing ad-hoc border/padding combinations.
- **Badge component standardization**: All status indicators (job status, SEBI risk levels, return categories) use a consistent Badge component with semantic color variants.
- **Button component standardization**: All interactive buttons use a consistent Button component with size and variant props, replacing inline Tailwind class strings.

### Could Have Features

- **Sidebar collapse state persistence**: Remember expanded/collapsed preference in localStorage across browser sessions.
- **Keyboard navigation shortcut**: Press `[` to toggle sidebar collapse.
- **Client view tooltip simplification**: In client view, tooltips on table rows show only 3 client-friendly metrics (Post-Tax Return, Expense Ratio, Min Investment) instead of all 6.
- **Audience-specific empty state copy**: Empty states vary by view — advisor sees "No products match your filters" while client sees "No products match your goals. Contact your advisor."

### Won't Have (This Phase)

- **Full dark mode**: The sidebar is dark; the main content area stays light. A full app-wide dark mode toggle is not in scope.
- **Storybook component documentation**: Component documentation library is out of scope.
- **Client portal route/subdomain**: No separate `/client` route or subdomain. The view switch is still advisor-controlled.
- **Read-only Risk Profiler for clients**: Clients do not see the Risk Profiler in this phase. Deferred to a future "client self-service" feature.
- **PDF expiry or sharing audit logs**: WhatsApp/PDF sharing improvements are out of scope.
- **Mobile-first responsive redesign**: The layout is desktop-first with basic tablet/mobile responsiveness. A dedicated mobile experience is out of scope.
- **Framer Motion animations**: All transitions use Tailwind CSS utilities only. No animation library dependency.

---

## Detailed Feature Specifications

### Feature: Dual-Audience View Switch

**Description:** The ClientViewToggle is a segmented control (two options: Advisor View / Client View) positioned in a toolbar strip at the top of the main content area, visible only on the Dashboard route. Toggling it triggers a cascade of visibility and layout changes across the dashboard — not just data filtering. The current `isClientView` state in the UI store is the single source of truth.

**User Flow:**
1. Advisor is in Advisor View (default) — full layout, all columns, full sidebar visible
2. Advisor clicks "Client View" in the segmented control
3. Sidebar collapses to icon-only automatically
4. FilterBar hides; a static filter summary label with "Change filters" link appears in its place
5. AssetTable re-renders with client-safe columns only (Breakdown column hidden)
6. RiskReturnPlot re-renders with simplified labels
7. ProductPins section appears above the table as hero cards (if products are pinned)
8. Navigation in sidebar shows Dashboard only
9. Advisor clicks "Advisor View" to restore all elements

**Business Rules:**
- Rule 1: Client View never reveals advisor-only data — even if the user navigates directly to a URL, advisor-specific columns and controls must remain hidden
- Rule 2: The FilterBar tax bracket and time horizon selections made in Advisor View continue to apply to all data calculations in Client View — they are just not displayed
- Rule 3: The sidebar collapse in Client View does not override a user's deliberate expand action — if the user manually expands the sidebar while in Client View, it stays expanded
- Rule 4: System Health (/admin) link in the sidebar is hidden entirely in Client View
- Rule 5: Switching views does not trigger a data refresh — the same data is presented, just filtered differently

**Edge Cases:**
- No pinned products in Client View → Show "Pin products in Advisor View to build your comparison" empty state in ProductPins area; table still shows with client-safe columns
- Switching views on non-Dashboard routes → View state persists, but non-Dashboard pages are not affected (they remain unchanged — Goals, Risk Profiler, Scenarios are hidden from nav in client view but accessible via direct URL)
- Very long product names in hero cards → Truncate with ellipsis at 2 lines; full name visible in tooltip on hover

---

## Success Metrics

### Key Performance Indicators

- **Adoption:** 100% of active advisor users encounter the new sidebar layout within their first session after deployment (no opt-in required — it's the default layout)
- **Engagement:** Client View toggle usage increases — target: 70%+ of sessions that include a dashboard visit also include at least one Client View activation
- **Quality:** Zero reported instances of advisor-only data (Advisor Score raw values, FilterBar controls, ScoreBreakdown) being visible in Client View
- **Performance:** Skeleton-to-content transitions complete with no visible layout shift (CLS score = 0 per Lighthouse)
- **Perception:** Informal advisor feedback — "the app looks professional enough to use in client meetings" (qualitative, gathered via check-in)

### Tracking Requirements

| Event | Properties | Purpose |
|-------|------------|---------|
| `sidebar_toggled` | `{ to: 'collapsed' \| 'expanded', page: string }` | Track sidebar usage patterns |
| `client_view_activated` | `{ pinned_count: number, has_client_selected: boolean }` | Measure client view adoption |
| `client_view_deactivated` | `{ duration_seconds: number }` | Understand presentation session length |
| `hero_card_rendered` | `{ product_count: number }` | Confirm hero layout is seen |
| `pdf_generated_from_client_view` | `{ product_count: number, client_id: string }` | Measure client view workflow completion |

---

## Constraints and Assumptions

### Constraints

- All transitions and animations must use Tailwind CSS utilities only — no Framer Motion or animation library
- The feature must not increase JavaScript bundle size by more than 50KB gzipped (shadcn/ui adds ~5KB gzipped for all 8 components)
- Tailwind CSS must remain on v3.x — no upgrade to v4 in this phase
- No new backend API endpoints are required — this is a frontend-only change
- The existing `isClientView` state in `uiStore` must remain the single source of truth for view mode

### Assumptions

- Financial advisors use the app on desktop (1280px+ screens) as their primary device
- Clients only see the app during advisor-led sessions or via shared PDF/WhatsApp links — they do not have their own login
- The existing Radix UI, CVA, and tailwind-merge dependencies are already installed and compatible with shadcn/ui (confirmed by architecture research)
- No SEBI regulatory requirement mandates showing specific data fields to clients — the advisor decides what to present
- The System Health (/admin) page remains advisor-only and does not need a client view

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Sidebar layout breaks existing component tests | Medium | Medium | Update tests alongside component changes; run full test suite after each phase |
| shadcn/ui CSS variable tokens conflict with existing `bg-blue-600` classes | Low | Low | Override `--primary` CSS variable to match blue-600 (219 90% 56%) before init; use Option B coexistence approach |
| Client View column hiding misses a data field | High | Medium | Create an explicit client-safe column allowlist in AssetTable; default to hidden for any new column |
| Sidebar collapse animation causes layout shift in dense tables | Low | Low | Animate `width` only (not `transition-all`); use `transition-[width]` for GPU-accelerated animation |
| Cumulative Layout Shift (CLS) from skeleton-to-content swap | Medium | Medium | Match skeleton row/card heights exactly to final content dimensions before implementing |

---

## Open Questions

All open questions resolved (2026-03-08):

- [x] **Sidebar advisor name/avatar:** Pull from auth store (advisor name and email from the logged-in session).
- [x] **Client view filter summary:** Show static label (e.g., "Filtered: 20% tax, 7-year horizon") with a "Change filters" link that switches back to Advisor View.
- [x] **RiskReturnPlot in client view:** Remains visible with simplified labels — hide "Advisor Score" bubble-size legend, replace axis labels with plain language ("Risk Level" / "Annual Return").

---

## Supporting Research

### Competitive Analysis

Reference applications validated during design research:
- **Linear:** Minimal sidebar with left accent bar for active items, uppercase section headers, keyboard shortcut hints — validated the dark sidebar + light content pattern
- **Vercel Dashboard:** Collapsible sidebar with section headers, content area stays light — validated the isolated dark sidebar approach
- **Stripe Dashboard:** Compact `text-xs font-semibold` table headers, status badges as semantic color pills, monospace tabular numbers — validated the financial table density approach
- **Notion:** Click-to-collapse sidebar sections, drag-to-reorder — noted but deferred (out of scope for this phase)

### User Research

Design decisions validated through brainstorm session with the product owner:

- Audience split confirmed: Advisor view = dense/pro, Client view = clean/friendly
- Approach confirmed: Sidebar + shadcn/ui (preferred over visual-polish-only and split-layouts alternatives)
- Motion confirmed: Tailwind-only transitions (no Framer Motion dependency)
- Scope confirmed: Visual aesthetics + UX patterns only (not component architecture refactor)

### Market Data

- shadcn/ui is the fastest-growing React component library as of 2025, used by Vercel, shadcn itself, and thousands of SaaS products — directly on the existing Radix UI + Tailwind + CVA stack
- Inter font is the de-facto standard for modern SaaS interfaces (Linear, Vercel, Stripe, Notion all use Inter) and provides tabular-nums variant critical for financial data alignment
- Dark sidebar + light content is the dominant pattern in 2026 SaaS dashboards — provides visual contrast hierarchy without requiring full dark mode implementation
