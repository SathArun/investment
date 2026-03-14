---
title: "Dark Mode Completion and Data Ingestion Recovery"
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
- [x] No feature redundancy (check for duplicates)
- [x] No technical implementation details included
- [x] A new team member could understand this PRD

---

## Product Overview

### Vision

Deliver a fully consistent dark-mode UI and reliable nightly market data ingestion so that advisors can work in a polished, low-eye-strain environment with scores that reflect up-to-date mutual fund and NPS data.

### Problem Statement

Two independent regressions are degrading the platform:

1. **Dark Mode Gaps:** The app ships a dark theme but seven components (Risk Profiler, Admin Job cards, Scenario Planner pages, Product Pins, Filter Summary) render with hardcoded white/gray backgrounds and text. Advisors who prefer dark mode see jarring light islands that look broken and unprofessional.

2. **Silent Data Staleness:** Three of the six nightly ingestion jobs — AMFI NAV, mfapi historical backfill, and NPS returns — have been failing to insert data. This silently corrupts the scoring engine's inputs: the 30,000+ pre-computed score combinations fed to the dashboard may use stale or absent prices. The NPS failure is confirmed architectural (JavaScript-rendered source); AMFI and mfapi are returning no data despite multiple fix attempts.

### Value Proposition

- **Advisors** get an environment they trust: the UI looks intentional on any theme, and the scores they show clients are backed by current data.
- **Platform integrity:** data freshness is a compliance-adjacent concern — presenting stale scores without disclosure would undermine the SEBI-compliant positioning.

---

## User Personas

### Primary Persona: Registered Investment Advisor (RIA)

- **Demographics:** Financial professional, 30–55, uses the platform daily on a desktop browser; typically prefers dark mode for long sessions.
- **Goals:** Present up-to-date product recommendations and risk-adjusted scores to clients; generate PDF compliance packs.
- **Pain Points:**
  - Switching between the dashboard (dark) and the Risk Profiler or Scenario Planner (light) is visually jarring and reduces credibility in client-facing sessions.
  - Scores presented to clients may be based on data that hasn't updated in days with no visible warning.

### Secondary Personas

None beyond the RIA for this issue. Admin users who monitor the Job Dashboard are the same persona in a different workflow.

---

## User Journey Maps

### Primary User Journey: Dark Theme Client Session

1. **Awareness:** Advisor opens the app in dark mode before a client meeting.
2. **Consideration:** Navigates to Risk Profiler to walk client through questionnaire — page snaps to white background.
3. **Friction:** Advisor notices the mismatch; client perceives it as a half-finished product.
4. **Desired Outcome:** All pages render consistently in the chosen theme; the advisor can run the full client workflow without jarring theme breaks.

### Secondary User Journey: Admin Monitors Data Freshness

1. **Awareness:** Admin checks the Job Dashboard after nightly jobs run.
2. **Consideration:** Sees AMFI, mfapi, and NPS jobs reporting 0 records inserted.
3. **Friction:** No actionable error detail; unclear whether data is stale or whether a fallback was used.
4. **Desired Outcome:** Jobs succeed with a non-zero record count; or on failure, the dashboard shows a clear staleness warning with the date of the last successful data.

---

## Feature Requirements

### Must Have Features

#### Feature 1: Full Dark Mode Coverage

- **User Story:** As a registered advisor, I want every page and component to honour the selected theme so that my client sessions look polished and consistent.
- **Acceptance Criteria:**
  - [ ] Given the app is in dark mode, When I open the Risk Profiler questionnaire, Then the background, labels, and input borders all use dark theme colours (no white or light-gray backgrounds visible).
  - [ ] Given the app is in dark mode, When I open the Admin Job Dashboard, Then job status badges render in dark-compatible colours (no light-green or light-red pill backgrounds).
  - [ ] Given the app is in dark mode, When I open the Scenario Planner (SIP Modeler and Stress Test tabs), Then all cards and text use dark theme tokens.
  - [ ] Given the app is in dark mode, When I open the Product Pins panel, Then all surfaces use dark theme tokens.
  - [ ] Given the app is in dark mode, When I view the Filter Summary, Then all labels and borders use dark theme tokens.
  - [ ] Given the app is in light mode, When I view any of the above components, Then the appearance is unchanged from today.

#### Feature 2: AMFI NAV Ingestion — Reliable Daily Update

- **User Story:** As a platform operator, I want the nightly AMFI mutual fund NAV job to insert at least 1,000 NAV records per run so that product scores reflect the latest prices.
- **Acceptance Criteria:**
  - [ ] Given the job runs at 23:30 IST, When the job completes successfully, Then ≥1,000 NavHistory records are inserted or updated for that date.
  - [ ] Given the job fails after all retries, When the Job Dashboard is viewed, Then the run shows a clear error status with the HTTP response code or failure reason.
  - [ ] Given the job has previously succeeded, When the current run fails, Then the last-successful-date is visible in the Job Dashboard and the failure does not crash the scheduler.

#### Feature 3: mfapi Historical Backfill — Reliable Weekly Run

- **User Story:** As a platform operator, I want the historical NAV backfill job to progressively fill gaps for schemes with less than one year of data so that CAGR and Sharpe calculations have adequate history.
- **Acceptance Criteria:**
  - [ ] Given the job runs on Sundays at 02:00 IST, When the job completes, Then ≥1 NavHistory record is inserted for at least one scheme.
  - [ ] Given a scheme returns HTTP 429, When the job encounters it, Then it backs off and retries that scheme before moving on rather than skipping silently.
  - [ ] Given the job runs longer than 30 minutes (batch cap hit), When it stops mid-batch, Then the next run continues from where it left off rather than restarting from scratch.

#### Feature 4: NPS Returns — Weekly Data Availability

- **User Story:** As a platform operator, I want NPS fund returns (1Y, 3Y, 5Y) to be available and current so that NPS products can be scored alongside mutual funds.
- **Acceptance Criteria:**
  - [ ] Given the job runs on Mondays at 07:00 IST, When it completes successfully, Then IndexHistory records exist for at least the SBI, LIC, UTI, HDFC, and Kotak PFMs across Equity, Corporate Bond, and Government Securities schemes.
  - [ ] Given the underlying data source is unavailable, When the job fails, Then the previous week's NPS data is retained (no records are deleted) and the failure is logged.
  - [ ] Given no endpoint has been found for NPS data, When the fallback static seed is used, Then the data is no more than 30 days stale.

### Should Have Features

- **Improved job run logging:** Each job run records the number of records inserted, skipped, and failed — visible in the Job Dashboard run history.
- **Staleness indicator:** The dashboard shows a "data as of [date]" notice on the product list when the last successful AMFI run is >24 hours ago.

### Could Have Features

- **Retry-on-startup:** If the previous night's job failed, auto-retry once at 06:00 IST before the trading day begins.
- **Slack/email alert:** Notify the operator email when any ingestion job fails two consecutive runs.

### Won't Have (This Phase)

- Headless browser (Playwright/Selenium) for scraping JS-rendered pages.
- Paid third-party data APIs.
- Real-time NAV updates (nightly batch is sufficient).
- Changes to the scoring engine weights or computation logic.

---

## Detailed Feature Specifications

### Feature: NPS Returns Data Availability

**Description:** The NPS Trust website renders fund return data via JavaScript (Highcharts). The current BeautifulSoup scraper retrieves 0 records. The requirement is for NPS return data (1Y, 3Y, 5Y per PFM per scheme type) to be available weekly regardless of how the source is accessed.

**User Flow (Operator perspective):**
1. Monday morning: scheduler triggers the NPS job at 07:00 IST.
2. Job fetches NPS return data from the selected source.
3. Job upserts IndexHistory records using the `NPS_{PFM}_{SCHEME}_{HORIZON}` ticker format.
4. Admin views Job Dashboard — run shows records inserted count.

**Business Rules:**
- NPS data must cover all five major PFMs: SBI, LIC, UTI, HDFC, Kotak.
- Returns stored as decimal fractions (e.g., 0.1552 for 15.52%).
- If source data is unavailable, retain previous records — never delete NPS history on a failed run.
- Data may be up to 7 days stale (weekly publication cadence is acceptable).

**Edge Cases:**
- Source endpoint changes format → scraper must log a parse error and retain old data.
- New PFM added by PFRDA → job should insert it without code changes (dynamic PFM discovery).
- Return value is negative → must be stored and not filtered out.

---

## Success Metrics

### Key Performance Indicators

- **Dark Mode Coverage:** 0 components with hardcoded light-only Tailwind classes after the fix (measured by code review and visual regression).
- **AMFI Job Success Rate:** ≥95% of scheduled runs insert ≥1,000 records within 30 days of release.
- **mfapi Job Success Rate:** ≥80% of scheduled runs insert ≥1 record within 30 days of release.
- **NPS Job Success Rate:** ≥90% of scheduled runs insert records for ≥5 PFMs within 30 days of release.
- **Data Freshness:** Dashboard "data as of" date is never >48 hours behind current date for >5% of advisor sessions.

### Tracking Requirements

| Event | Properties | Purpose |
|-------|------------|---------|
| `job_run_completed` | job_name, records_inserted, records_skipped, duration_ms, success | Track ingestion reliability over time |
| `job_run_failed` | job_name, error_code, error_message, consecutive_failures | Alert on persistent failures |
| `dark_mode_theme_applied` | component_name, theme | Verify all components respond to theme changes (QA use only) |

---

## Constraints and Assumptions

### Constraints

- No new Python dependencies that add >50MB to the Docker image (rules out headless browsers for NPS).
- No paid external data APIs — all sources must be free/public.
- SEBI compliance records (PDF/compliance packs) must not be affected by this change.
- Dark mode fix must not alter any light-mode visual appearance.

### Assumptions

- The NPS Trust website's Highcharts page calls a discoverable backend endpoint that can be called directly without a browser session.
- If no such endpoint is found, static JSON with monthly manual update is an acceptable interim fallback.
- The AMFI plain-text endpoint (`amfiindia.com/spages/NAVAll.txt`) is still live and the failure is a client-side issue (headers, timeout), not an endpoint removal.
- mfapi.in (`mfapi.in/mf/{scheme_code}`) is still operational and the failure is due to rate limiting or per-scheme errors, not an API shutdown.

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| NPS endpoint is session-authenticated (cannot be called directly) | High | Medium | Fall back to static JSON seed with documented manual refresh process |
| AMFI changes the NAVAll.txt format | High | Low | Add format version detection; fail fast with clear parse error |
| mfapi.in shuts down or introduces auth | High | Low | Document alternative (AMFI scheme-code lookup + direct historical import) |
| Dark mode token swap introduces visual regression in light mode | Medium | Low | Side-by-side screenshot comparison before merge; smoke-test both themes |
| Batch cap on mfapi causes some schemes to never backfill | Medium | Medium | Implement cursor-based batching (remember last processed scheme_code) |

---

## Open Questions

- [ ] Has the NPS Trust network tab been inspected to identify the underlying data endpoint URL? (Needs investigation before SDD.)
- [ ] Is there a preferred alternative free API for mutual fund historical NAVs if mfapi.in is unreliable? (Decision needed before SDD.)
- [ ] Should AMFI and mfapi share a common retry/backoff utility, or is per-job handling sufficient?

---

## Supporting Research

### Competitive Analysis

Not applicable — this is a bug-fix and reliability improvement, not a new user-facing feature competing in a market.

### User Research

Validated through direct advisor feedback (the user/operator is the primary stakeholder). The dark mode gaps are visually confirmed. The ingestion failures are confirmed in job logs (0 records inserted).

### Market Data

- AMFI publishes NAVAll.txt daily; it is the canonical source for Indian mutual fund NAVs and is used by mfapi.in itself.
- NPS returns are published weekly by NPSTRUST; the data changes slowly.
- mfapi.in is a well-known free community API for historical Indian mutual fund data with no SLA.
