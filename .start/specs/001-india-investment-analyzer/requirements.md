---
title: "India Investment Analyzer — Financial Advisor Platform"
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

Empower Indian financial advisors (RIAs/MFDs/IFAs) to deliver faster, more credible, and SEBI-compliant investment recommendations by providing the only platform that ranks every investable asset class in India on a unified, tax-adjusted, risk-adjusted basis — with one-click client-ready presentations.

### Problem Statement

Indian financial advisors spend 30–45 minutes per client meeting manually aggregating data from 4–6 separate platforms (Value Research Online, Moneycontrol, AdvisorKhoj, Tickertape, AMFI, NPSTRUST) to produce a cross-asset investment picture that still arrives in a clunky Excel sheet or improvised PowerPoint. No single tool in India compares mutual funds, fixed deposits, PPF, NPS, gold, REITs, bonds, and equities on a common scoring basis that accounts for India's complex tax rules (LTCG, slab-rate debt taxation, EEE status, SGB tax-free maturity). This gap costs advisors 2–4 hours per week and limits their ability to defend multi-asset recommendations confidently to clients. Regulatory risk compounds the problem: SEBI mandates documented risk profiling, suitability rationale, and 5-year record retention — obligations most advisors fulfill via paper or ad-hoc PDFs. The consequence is lower client trust, reduced AUM per advisor, and real compliance exposure.

**Evidence:**
- India has ~1,200–1,500 SEBI-registered RIAs managing ~Rs 5.5 lakh crore in direct AUM as of December 2025
- Advisors preparing for client meetings spend 30–40% of prep time on data aggregation alone (user research)
- The MF industry crossed Rs 81 lakh crore AUM in January 2026; TAM for advisor tooling is growing 22%+ YoY
- No Indian platform scores or compares all asset classes on a unified risk-adjusted and tax-adjusted basis (competitive analysis)
- Top MFDs earn ~Rs 6.7 crore annually, making a Rs 1–2 lakh/year tooling cost highly justifiable

### Value Proposition

India Investment Analyzer is the first platform to:
1. **Rank all Indian asset classes on one screen** — equities, mutual funds, FDs, PPF, NPS, gold, REITs, bonds, commodities — using a composite Advisor Score
2. **Show post-tax returns instantly** — apply the client's income tax bracket to every product comparison automatically
3. **Turn research into presentations in seconds** — one-click branded PDF reports and WhatsApp-ready summaries, replacing hours of manual slide preparation
4. **Document SEBI compliance automatically** — generate audit-ready risk profiling packs and suitability rationale records

---

## User Personas

### Primary Persona: Arjun — Independent Financial Advisor (IFA/MFD)

- **Demographics:** 35–52 years, AMFI-registered Mutual Fund Distributor, manages 80–200 client families, Tier-1 or Tier-2 city, moderate-to-strong tech comfort, uses WhatsApp Business daily, earns primarily from trail commissions
- **Goals:** Grow AUM per client from Rs 15L to Rs 40L+ by expanding conversations from mutual funds to multi-asset; reduce prep time per client meeting from 2 hours to 30 minutes; impress new prospective clients with sophisticated, data-backed presentations; stay SEBI-compliant without hiring a compliance officer
- **Pain Points:** Data scattered across 5+ platforms; no cross-asset comparison tool; WhatsApp is the primary client communication channel but most tools only export to email; SEBI compliance documentation is a growing burden; clients keep comparing returns to FDs and he has no visual tool to counter this in real time

### Secondary Personas

**Priya — SEBI-Registered Investment Adviser (RIA)**
- **Demographics:** 30–45 years, fee-only fiduciary advisor, SEBI IA registration, manages 50–100 clients at higher AUM (Rs 50L+), strong analytical skills, serves HNI (High Net-worth Individual) clientele
- **Goals:** Demonstrate fiduciary rigor with documented, evidence-based recommendations; generate compliance-grade suitability rationale for every product advised; offer sophisticated scenario planning (retirement, goal-based Monte Carlo) that justifies premium fees
- **Pain Points:** No single tool produces audit-ready suitability documentation; risk-adjusted metrics (Sharpe, Sortino, Calmar) are only available per-asset-class in silos; HNI clients expect stress-tested portfolio analysis that no Indian advisor tool currently provides

**Ravi — Wealth Management Associate at a Small Advisory Firm**
- **Demographics:** 25–35 years, analyst/associate at a boutique wealth management firm, technically comfortable, handles research and client report preparation for 3–5 senior advisors
- **Goals:** Cut report preparation time; maintain consistent firm-branded output; pull accurate data without manual cross-checking
- **Pain Points:** Manual work is repetitive and error-prone; firm-branded output requires Word/PowerPoint editing after every data pull; no API or batch export to feed the firm's internal CRM

---

## User Journey Maps

### Primary User Journey: Pre-Meeting Client Preparation

1. **Awareness:** Arjun has a review meeting tomorrow with Sharma, a 45-year-old moderate-risk client. Sharma's portfolio is 80% equity MFs, and he's been asking whether FDs or gold might be safer amid market noise.
2. **Consideration:** Arjun currently opens Value Research Online for MF data, Moneycontrol for market context, and manually computes post-tax returns in Excel. He spends 90 minutes on this. He's heard about the platform from a peer advisor at an AMFI regional event.
3. **Adoption:** Arjun logs in, enters Sharma's profile (age 45, tax bracket 30%, risk profile Moderate, goal: retirement in 15 years), and within 5 minutes sees a ranked comparison of large-cap equity, balanced advantage, gold ETF, corporate bond fund, and FD — all scored and post-tax adjusted for Sharma's 30% bracket.
4. **Usage:** He filters by "Moderate" risk, sees the top 5 options with 1Y/3Y/5Y returns, Sharpe ratios, post-tax yields, and liquidity scores. He pins the top 3 for the client presentation. He clicks "Generate Client PDF" — branded with his firm's logo — and shares it on WhatsApp before the meeting.
5. **Retention:** After the meeting, Arjun documents the risk profile and suitability rationale in the platform's compliance module, exports the audit PDF, and saves it to the client's record. He does this every quarter. The platform has replaced Excel and 3 other tools.

### Secondary User Journeys

**Journey: Live Client Meeting — Advisor Presentation Mode**
1. During the meeting, Arjun switches the platform to "Client View" mode — a clean, jargon-free interface with plain-language risk labels ("Your money could dip 25% in a bad year but historically recovered within 18 months")
2. He uses the interactive risk-return scatter plot to visually show Sharma where large-cap equity sits vs FD vs gold
3. He runs a live SIP scenario: "What if you add Rs 10,000/month for 15 years at 12% vs 8% returns?" — the compounding chart updates instantly
4. Sharma understands and approves; Arjun exports a one-page "Today's Recommendations" summary and sends it to Sharma's WhatsApp before Sharma leaves

**Journey: SEBI Compliance Documentation**
1. Priya completes a risk profiling session with a new client using the platform's guided questionnaire
2. The platform generates a dated compliance PDF: client responses, calculated risk score, risk category communication, and Priya's typed suitability rationale for each recommendation
3. Priya signs off digitally; the document is stored with a 5-year retention timestamp
4. During a SEBI audit, Priya exports the full compliance pack for any client in one click

---

## Feature Requirements

### Must Have Features

#### Feature 1: Multi-Asset Class Investment Dashboard

- **User Story:** As an advisor, I want to see all Indian investable asset classes ranked side-by-side by returns and risk so that I can identify the best options for my client in under 5 minutes without opening multiple platforms.
- **Acceptance Criteria:**
  - [ ] Given the advisor is logged in, When they open the dashboard, Then they see a sortable table with at least 12 asset class categories: Large-Cap Equity, Mid-Cap Equity, Small-Cap Equity, Flexi/Multi-Cap Equity, Debt MF (short/medium/long duration), Liquid Funds, Bank FDs, PPF, NPS, Gold (ETF/SGB/Fund), REITs, and Government Bonds
  - [ ] Given the dashboard is loaded, When the advisor sorts by "3Y CAGR", Then rows reorder instantly (< 1 second) and the sort column is visually highlighted
  - [ ] Given any asset class row, When the advisor hovers, Then a tooltip shows: 1Y, 3Y, 5Y, 10Y returns, standard deviation, max drawdown, expense ratio, minimum investment, SEBI risk level, and liquidity rating
  - [ ] Given the advisor selects a tax bracket (0%, 5%, 10%, 20%, or 30%), When they apply it, Then all return columns update to show post-tax returns for that bracket across all asset classes simultaneously
  - [ ] Given data from AMFI, yfinance, or cached sources, When the page loads, Then data refresh timestamps are displayed for each data category and data is no older than 24 hours for mutual fund NAVs

#### Feature 2: Composite Advisor Score

- **User Story:** As an advisor, I want each investment option to have a single composite score so that I can justify my recommendation with a defensible, multi-factor rationale.
- **Acceptance Criteria:**
  - [ ] Given any investment product in the dashboard, When it is displayed, Then a composite Advisor Score (0–100) is shown, derived from six sub-scores: risk-adjusted return (Sharpe/Sortino normalized), tax-adjusted net yield (at the set tax bracket), liquidity score, cost/expense score, consistency score (rolling return variance), and goal-fit score (based on selected time horizon)
  - [ ] Given the advisor changes the time horizon filter (Short: 0–3Y, Medium: 3–7Y, Long: 7Y+), When applied, Then the goal-fit sub-score updates and the composite score re-ranks accordingly
  - [ ] Given any Advisor Score shown, When the advisor clicks "Score Breakdown", Then a panel opens showing the six sub-scores individually with plain-language explanations of each
  - [ ] Given a score is displayed, When a client presentation is generated, Then the score breakdown appears in plain language (e.g., "High Liquidity — you can exit this investment within 1 business day") without numerical sub-scores visible to the client

#### Feature 3: Tax Overlay Engine

- **User Story:** As an advisor, I want to enter my client's income tax bracket and see post-tax returns for every product so that I can show the real comparison that matters to the client.
- **Acceptance Criteria:**
  - [ ] Given the advisor enters a tax bracket (0%/5%/10%/20%/30%), When applied, Then the system correctly calculates post-tax returns using the correct rule for each asset class: Equity LTCG at 12.5% (above Rs 1.25 lakh annual threshold), Equity STCG at 20%, Debt MF at slab rate, Gold ETF at 12.5% LTCG or slab STCG, SGB as tax-free at maturity, PPF as EEE, NPS Tier 1 as 60% lump sum tax-free
  - [ ] Given the tax overlay is active, When the advisor views the dashboard, Then a clearly visible banner says "Post-tax returns shown — Tax bracket: 30%" so the advisor does not confuse pre-tax and post-tax figures
  - [ ] Given a client in the 30% tax bracket, When comparing a 7% FD vs a 7% debt mutual fund, Then the system shows the FD returning 4.9% post-tax and the debt MF returning approximately 4.9% post-tax (slab rate), with the difference being the expense ratio and liquidity
  - [ ] Given SGB vs Gold ETF comparison, When a client is in any tax bracket, Then SGB (held to maturity) shows higher post-tax return than Gold ETF, correctly reflecting the tax-free maturity benefit

#### Feature 4: Client Presentation Mode

- **User Story:** As an advisor, I want to switch to a clean, jargon-free view and generate a branded PDF in one click so that I can show clients professional analysis without exposing complex advisor-only metrics.
- **Acceptance Criteria:**
  - [ ] Given the advisor clicks "Client View", When the mode activates, Then all Sharpe ratios, standard deviations, and numerical sub-scores are hidden; plain-language risk labels appear (e.g., "LOW — Your principal is very safe; returns vary slightly"; "HIGH — Returns can drop 40–50% in bad years but have historically recovered over 7+ years")
  - [ ] Given the advisor has selected 3–5 products to compare, When they generate a PDF, Then the PDF contains: advisor's logo and contact details (configurable), today's date, client name (if entered), the selected comparison table with returns and plain-language risk labels, a mandatory SEBI disclaimer, and a summary recommendation section
  - [ ] Given a generated PDF, When the advisor clicks "Share via WhatsApp", Then the platform opens a WhatsApp share dialog with the PDF attached and a pre-filled message template the advisor can edit before sending
  - [ ] Given a client presentation is generated, When it is exported, Then it does not contain the advisor's internal Advisor Score breakdown, proprietary scoring weights, or detailed sub-score calculations

#### Feature 5: Goal-Based Planner

- **User Story:** As an advisor, I want to enter a client's goal parameters and see the required SIP, recommended asset allocation, and product suggestions so that I can build a complete financial plan in minutes.
- **Acceptance Criteria:**
  - [ ] Given the advisor enters: goal name, target amount (in Rs), target date, current savings, and monthly SIP capacity, When they submit, Then the system calculates: inflation-adjusted target corpus, gap between current trajectory and target, required SIP amount to close the gap at expected returns, probability of achieving the goal
  - [ ] Given a goal time horizon, When recommendations are generated, Then asset allocation follows the goal-fit framework: 0–3 years → primarily liquid and debt options; 3–7 years → balanced/hybrid + debt; 7+ years → predominantly equity with defined debt allocation
  - [ ] Given a 15-year retirement goal with a 30% tax bracket, When the advisor runs the planner, Then NPS Tier 1 appears as a highlighted option with the note "Additional Rs 50,000 deduction under Section 80CCD(1B)"
  - [ ] Given any SIP calculation, When the advisor adjusts the "Annual Step-Up %" field, Then the projected corpus updates instantly showing the incremental benefit of increasing SIP contribution annually

#### Feature 6: SEBI-Compliant Risk Profiling Suite

- **User Story:** As a SEBI-registered advisor, I want to conduct a documented risk profiling session and generate an audit-ready compliance PDF so that I can satisfy SEBI IA Regulations without manual documentation work.
- **Acceptance Criteria:**
  - [ ] Given a new client record, When the advisor starts a risk profiling session, Then a guided 15–20 question questionnaire captures: age, income and income stability, existing assets and liabilities, investment objectives, investment horizon per goal, risk appetite (behavioral questions including "sleep test" style scenarios), and liquidity needs
  - [ ] Given completed questionnaire responses, When the system calculates the risk score, Then it outputs one of five risk categories: Conservative, Moderately Conservative, Moderate, Moderately Aggressive, Aggressive — with a written description of each category
  - [ ] Given a completed risk profile, When the advisor clicks "Generate Compliance Pack", Then a PDF is produced containing: client's name and date, all questionnaire questions and responses, calculated risk score, assigned risk category, the advisor's typed suitability rationale (editable text field), a space for client and advisor digital acknowledgment, and a timestamp
  - [ ] Given a generated compliance pack, When stored in the platform, Then it is retained with a minimum 5-year timestamp and is retrievable via search by client name or date

### Should Have Features

- **Portfolio Stress Test:** Show estimated impact of three historical stress scenarios on a selected portfolio or product mix — COVID 2020 crash (Nifty -38%, recovery 8 months), 2008 Global Financial Crisis (Nifty -60%, recovery 28 months), 2022 Rate Hike Cycle (debt fund NAV impact). Displays estimated drawdown and historical recovery timeline.
- **Scenario Planner:** Interactive what-if tools: (a) SIP modeler — change monthly amount, expected return, or duration and see updated corpus; (b) Interest rate sensitivity — show debt fund NAV impact if rates rise/fall 50–100 bps; (c) Retirement withdrawal simulator — how long does a corpus last at different monthly withdrawal amounts?
- **Portfolio Overlap Checker:** Input 3–10 mutual fund names; system shows stock-level overlap percentage between funds and flags unintentional concentration.
- **Rolling Return Comparison:** For any asset class or fund, display rolling 1Y, 3Y, 5Y return distribution as a chart showing minimum, median, and maximum rolling return over historical periods — to counter point-to-point return bias.
- **SEBI Disclaimer Auto-Injection:** All generated PDFs and client-facing outputs automatically include the correct SEBI-mandated disclaimer text: "Investment in securities market are subject to market risks. Read all the related documents carefully before investing."

### Could Have Features

- **Client Portal (Read-Only):** A mobile-responsive view where clients can see their named goals, progress percentages, and portfolio summary — without advisor-only analytics. Share link sent via WhatsApp.
- **Multi-Client Management:** Advisor dashboard showing all client profiles, their risk categories, goal statuses, and last review date — replacing Excel-based CRM for smaller advisors.
- **Tax Harvesting Alert:** Flag when a client's unrealized LTCG approaches Rs 1.25 lakh annual threshold and prompt the advisor to book gains and reinvest (saves future tax without triggering current tax).
- **WhatsApp Monthly Summary:** Automated generation of a one-page portfolio health summary for each client on a set cadence, ready to send via WhatsApp.
- **Branding Customization:** Advisor can upload logo, set primary color, and configure firm name/contact details that appear on all generated client PDFs.
- **Data Export:** Export any comparison table or client report as Excel for advisors who need to feed data into their own models.

### Won't Have (This Phase)

- **Transaction execution or order placement** — no brokerage or payment integration; read-only market data only
- **Real-time live price streaming** — end-of-day pricing is sufficient; intraday data not required
- **Portfolio import via CAMS/KFintech CAS statement** — valuable but complex; deferred to Phase 2
- **Insurance analysis or product comparison** — IRDAI-regulated products are out of scope; advisor can reference separately
- **PMS (Portfolio Management Services) analysis** — minimum Rs 50 lakh threshold segment deferred to Phase 2
- **Cryptocurrency portfolio tracking** — crypto is flagged as a Very High Risk category in the dashboard for informational purposes only; no portfolio tracking
- **US stocks / international equity** — covered at category level in the dashboard as "International Equity Funds" via India-domiciled FOFs; direct international trading is out of scope
- **Multi-user team accounts** — Phase 1 is single-user per advisor; firm-level multi-seat access deferred

---

## Detailed Feature Specifications

### Feature: Composite Advisor Score Engine

**Description:** A normalized, multi-factor scoring system that assigns every investable product in India a single score from 0 to 100. The score synthesizes six dimensions — all weighted and combined — to allow true apples-to-apples comparison across radically different asset classes (e.g., a Gilt fund vs a Small-Cap equity vs a Bank FD). The score is contextualized by the advisor's current filters (time horizon, tax bracket, risk category).

**Score Component Definitions:**

| Sub-Score | Weight (default) | Computation Basis |
|---|---|---|
| Risk-Adjusted Return | 30% | Sharpe ratio and Sortino ratio normalized to 0–100 across all products in the same time horizon bucket |
| Tax-Adjusted Net Yield | 25% | Post-tax return at the selected tax bracket, normalized to 0–100 against peer asset classes |
| Liquidity Score | 15% | Exit load period, lock-in duration, market liquidity (for ETFs: bid-ask spread proxy), normalized to 0–100 |
| Cost/Expense Score | 10% | Total expense ratio (MFs), transaction cost (equities), or 0 (FDs/PPF/G-Secs), inverted and normalized to 0–100 |
| Consistency Score | 10% | Standard deviation of trailing annual returns over 5 years; lower variance scores higher |
| Goal-Fit Score | 10% | Alignment of the product's typical holding period and risk profile with the advisor's selected time horizon filter |

**User Flow:**
1. Advisor sets active filters: Time horizon = "Long (7Y+)", Tax bracket = "30%", Risk filter = "All"
2. System calculates Advisor Scores for all products using the weights above, applied to the selected horizon bucket's historical data
3. Dashboard displays products ranked by Advisor Score descending; advisor can also sort by any sub-score column
4. Advisor clicks "Score Breakdown" on a specific product → side panel opens showing individual sub-scores as labeled bar segments with plain-language descriptions
5. Advisor selects 3 products → clicks "Compare Selected" → comparison panel shows all sub-scores side by side

**Business Rules:**
- Scores are recalculated when the advisor changes any filter (time horizon, tax bracket, risk category); no stale scores displayed
- Products with fewer than 3 years of return history receive a "Consistency Score" of N/A and are flagged with a data availability badge
- PPF and G-Secs receive a Consistency Score of 100 (zero variance) because returns are government-set
- The Liquidity Score for NPS Tier 1 is set to 10 (lowest tier) reflecting lock-in until age 60 with limited withdrawal provisions
- SGB (Sovereign Gold Bond) receives two score variants: one for secondary-market exit (moderate liquidity) and one for hold-to-maturity (highest tax-adjusted yield)

**Edge Cases:**
- Debt MFs post the April 2023 rule change (no LTCG benefit): All debt mutual fund products are taxed at slab rate regardless of holding period — the Tax-Adjusted Yield score must not apply LTCG rates to any debt MF under any filter combination
- Annual LTCG exemption (Rs 1.25 lakh): When computing equity post-tax returns, the system assumes the first Rs 1.25 lakh of annual gains are tax-free. If the advisor has set a specific client investment amount, the system calculates whether gains exceed the threshold; otherwise it uses the default assumption that the threshold is partially used
- Zero expense ratio products (PPF, FDs, G-Secs via RBI Retail Direct): Cost/Expense Score = 100 for these; the score should not conflate low cost with low quality
- International equity funds: Subject to SEBI's overseas investment cap which has caused intermittent subscription freezes. Dashboard must flag these products when industry-wide AUM limits are reportedly near, and mark the Liquidity Score appropriately

---

## Success Metrics

### Key Performance Indicators

- **Adoption:** 50 active advisor accounts within 3 months of launch; 200 within 6 months
- **Engagement:** Average advisor generates ≥ 2 client PDFs per week; average session duration > 20 minutes
- **Quality:** < 2% data inaccuracy rate in return figures (validated monthly against AMFI and NSE reference data); zero compliance pack generation failures
- **Business Impact:** 80% of trial advisors convert to paid within 30 days; Net Promoter Score (NPS for the product) ≥ 50 by month 6

### Tracking Requirements

| Event | Properties | Purpose |
|-------|------------|---------|
| `dashboard_loaded` | time_to_load, asset_classes_visible, filter_state | Monitor performance; identify if advisors change defaults |
| `tax_bracket_set` | bracket_value, session_id | Understand most common tax contexts; validate Tax Overlay correctness |
| `product_pinned` | product_name, asset_class, advisor_score | Identify most-compared products; validate Advisor Score rankings |
| `pdf_generated` | client_age, risk_category, products_included, time_to_generate | Measure presentation feature adoption and speed |
| `whatsapp_share_clicked` | pdf_type, product_count | Confirm WhatsApp integration is used (primary sharing channel) |
| `risk_profile_completed` | risk_category_assigned, question_count, time_taken | Ensure risk profiling is thorough enough; flag sessions where ≤ 5 min spent |
| `compliance_pack_exported` | client_id_hash, date | Confirm compliance workflows are operationally trusted |
| `sip_scenario_run` | goal_horizon, step_up_percent, initial_corpus | Understand goal planning engagement depth |
| `advisor_score_breakdown_viewed` | product_name, sub_scores | Confirm advisors are using and trusting the composite score |

---

## Constraints and Assumptions

### Constraints

- **Data Sources:** The platform relies on free and low-cost public data sources in Phase 1 — AMFI NAV API, mfapi.in, Angel One SmartAPI (free with account), yfinance for NSE/BSE index data, and RBI/PFRDA published rate tables. Real-time data is not available from these sources; data is end-of-day.
- **Regulatory:** The platform is an information and research tool for advisors, not a registered Investment Adviser or Research Analyst entity itself. All content carries mandatory SEBI disclaimers. The platform does not provide personalized advice — the advisor does. This boundary must be maintained in all product copy, feature descriptions, and generated documents.
- **SEBI Compliance:** Risk profiling compliance packs generated by the platform are designed to assist advisors in meeting their own regulatory obligations; the platform does not warrant that generated documents satisfy any specific SEBI audit requirement. Advisors are responsible for their own compliance.
- **No Transaction Execution:** The platform is read-only for market data. No financial transactions can be initiated through the platform in Phase 1.
- **Performance:** Historical return calculations for rolling return charts require 5–10 years of data per product. The system must handle this data volume without exceeding 3-second load times for any dashboard or calculation.

### Assumptions

- **User Assumption:** Financial advisors (IFAs, MFDs, RIAs) are the primary users. The platform assumes a baseline financial literacy in the user — advisors understand terms like Sharpe ratio, CAGR, and LTCG without in-app definitions, though client-facing materials use plain language.
- **Market Assumption:** WhatsApp is the dominant client communication channel for Indian advisors. The "Share via WhatsApp" feature will be used for the majority of client communications rather than email.
- **Data Assumption:** AMFI's free NAV API (updated daily) and mfapi.in provide sufficient historical NAV data for rolling return calculations for all SEBI-registered mutual funds. Historical data for index funds/ETFs is available via yfinance.
- **Tax Assumption:** India's tax rules as of FY2025-26 are stable for the platform's initial version. Any future budget changes will require product updates; the platform will display the applicable tax year prominently so advisors know which rules are being applied.
- **Compliance Assumption:** SEBI IA Regulations 2013 (as amended through December 2024) are the applicable framework. The risk profiling questionnaire design follows SEBI's guidance on "fit for purpose" risk assessment.

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| AMFI or yfinance API unavailability causes stale data | High — advisors cannot trust figures in client meetings | Medium | Cache last-known data with clear staleness warnings; fallback to last 24-hour snapshot with timestamp displayed |
| Tax rule changes (annual Budget) invalidate core calculations | High — wrong post-tax returns shown | High (annual) | Modular tax rule engine designed for quick update; each rule has an effective date; alert advisors when rules are updated |
| SEBI redefines RIA/MFD regulatory boundaries in ways that affect feature scope | High — compliance documentation features may need redesign | Medium | Monitor SEBI circulars; build compliance features conservatively (assist, don't certify) |
| Advisors share platform access with clients (defeating the dual-mode design) | Medium — clients see advisor-only metrics; damages trust | Low | Client Presentation Mode URL is shareable and advisor-only mode requires login; design dual-mode with clear session management |
| Composite Advisor Score is gamed or misunderstood | Medium — advisors recommend based on score alone without judgment | Low | Always display individual sub-scores with score breakdown; include a disclaimer that the score is a research aid, not a recommendation |
| Free data API rate limits or deprecation | Medium — data gaps for specific asset classes | Medium | Identify paid backup sources (Angel One SmartAPI as fallback for equity data); maintain a manual override mechanism for PPF/FD rates |
| SEBI auditors reject platform-generated compliance packs as insufficient | High — advisor's regulatory standing at risk | Low | Engage a SEBI-compliant legal reviewer before launch to validate template; include explicit disclaimer on all compliance documents that the advisor is responsible for their own compliance |

---

## Open Questions

- [x] **Branding Tier:** Advisor branding (logo + contact details) included in base Phase 1 plan — no separate paid tier for this feature.
- [x] **Client Portal Access:** Phase 2. Phase 1 is advisor-only. No client-facing login or portal in scope.
- [ ] **NPS Data Integration:** NPSTRUST publishes weekly snapshots of NPS fund returns. Is weekly data sufficient for Phase 1, or is daily NPS NAV data required (available only through PFRDA-registered intermediaries)? → **Defaulting to weekly data (free)** for Phase 1.
- [x] **Real Estate Proxy:** REITs only (Embassy, Mindspace, Brookfield, Nexus). Physical real estate excluded from scored comparison — no reliable pricing API.
- [x] **Crypto Treatment:** Include crypto as "Very High Risk / Speculative" with mandatory regulatory risk disclaimer. Not portfolio-trackable; informational display only.

---

## Supporting Research

### Competitive Analysis

No Indian platform currently provides cross-asset-class unified scoring. Key competitive landscape:

| Platform | Multi-Asset | Advisor Workflow | Client Reports | Tax Integration |
|---|---|---|---|---|
| Value Research Online | Low (MF only) | None | None | None |
| Morningstar India | Low (funds) | Limited | Limited | None |
| Tickertape | Medium (stock+MF) | None | None | None |
| Screener.in | Low (equity only) | None | None | None |
| AdvisorKhoj | Low (MF) | Good | Good (MF branded) | None |
| Kuvera | Low (MF+FD+US) | None | None | Good (tax harvest) |
| **India Investment Analyzer** | **High (all classes)** | **Full** | **Full branded** | **Full** |

Nearest global analogues: YCharts (US), Morningstar Advisor Workstation (global), Orion (US) — none built for India's tax framework.

### User Research

Based on advisor workflow analysis:
- Advisors spend 30–40% of meeting prep time on data aggregation across 4–6 platforms
- WhatsApp is the primary advisor-client communication channel for 85%+ of Indian IFAs
- SEBI audit risk is a genuine operational anxiety — compliance documentation features are a "fear" motivator alongside "growth" motivators
- Plain-language risk communication tools (not Sharpe ratios) are what advisors need during client meetings
- SIP illustration charts are the single most persuasive tool for converting conservative clients to equity exposure

### Market Data

- India Mutual Fund AUM: Rs 81 lakh crore (January 2026), growing at 22%+ YoY
- Monthly SIP inflows exceeded Rs 25,000 crore by end 2024
- SEBI-registered RIAs: ~1,200–1,500 managing Rs 5.5 lakh crore direct AUM
- Top 3,158 MFDs earned an average of Rs 6.7 crore gross income in FY2025
- India wealth management AUM projected to reach USD 2.3 trillion by FY29
- India's advisor-to-population ratio is critically low vs developed markets — TAM is expanding rapidly
- WealthTech funding in India reached $634M in FY2024-25 (Entrackr)
