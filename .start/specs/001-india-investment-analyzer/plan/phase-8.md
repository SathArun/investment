---
title: "Phase 8: Goal Planner, Risk Profiler & Scenario UI"
status: completed
version: "1.0"
phase: 8
---

# Phase 8: Goal Planner, Risk Profiler & Scenario UI

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: PRD/Feature 5 Goal-Based Planner AC]` — Goal planner acceptance criteria
- `[ref: PRD/Feature 6 SEBI Risk Profiling AC]` — Risk profiling acceptance criteria
- `[ref: PRD/Should Have Features; Scenario Planner, Portfolio Stress Test]`
- `[ref: SDD/User Interface & UX; Screen Flow diagram]`
- `[ref: SDD/Internal API Changes; goals, risk profiler endpoints]`

**Key Decisions**:
- Goal planner step-up SIP update: client-side calculation for instant feedback (uses same formula as backend)
- Scenario planner tools (SIP modeler, rate sensitivity, retirement withdrawal) are client-side computations — no API call needed for basic what-if
- Portfolio stress test uses `data/reference/stress_scenarios.json` served via a static API endpoint

**Dependencies**:
- Phase 5 complete (Goal and Risk Profiler API)
- Phase 6 complete (Compliance PDF generation)
- Phase 7 complete (Auth, routing, Zustand, Shadcn/ui available)

---

## Tasks

Builds the Goal Planner module, Risk Profiler questionnaire with compliance export, and the Scenario Planner tools.

- [x] **T8.1 Goal planner form + corpus projection chart** `[activity: frontend-ui]`

  1. Prime: Read `[ref: PRD/Feature 5 AC]` — goal form fields, corpus projection, NPS highlight, step-up SIP
  2. Test: GoalForm renders all fields: goal name, target amount (Rs), target date, current corpus, monthly SIP, annual step-up %; submitting calls `POST /api/goals`; after creation, `GET /api/goals/{id}/plan` called automatically; corpus projection chart renders 3 lines (conservative/base/optimistic); changing "Annual Step-Up %" updates chart within 500ms without API call; NPS banner appears when `nps_highlight: true` in API response; goal added to client profile visible in client dropdown
  3. Implement: Create `src/components/GoalPlanner/GoalForm.tsx` with controlled form + React Hook Form validation; `src/components/GoalPlanner/CorpusChart.tsx` with Recharts AreaChart (3 series); `src/components/GoalPlanner/AllocationPie.tsx` with Recharts PieChart; client-side step-up formula for instant chart updates without re-fetch: `FV_stepup = SIP × [(1+r)^n - (1+g)^n] / (r - g)` where r = monthly return and g = monthly step-up rate; NPS banner component
  4. Validate: RTL: form submits correctly; chart updates on step-up change < 500ms; NPS banner appears for 15Y goal at 30% bracket; pie chart allocation segments sum to 100%; chart renders 3 distinct colored lines
  5. Success:
    - [x]Corpus projection chart shows conservative/base/optimistic scenarios `[ref: PRD/Feature 5 AC]`
    - [x]Step-up SIP chart updates instantly (client-side) `[ref: PRD/Feature 5 AC; step-up]`
    - [x]NPS highlighted with 80CCD(1B) note for qualifying goals `[ref: PRD/Feature 5 AC; NPS highlight]`

- [x] **T8.2 Risk profiler questionnaire UI** `[activity: frontend-ui]`

  1. Prime: Read `[ref: PRD/Feature 6 AC]` — 15-20 questions, risk score meter, compliance PDF trigger
  2. Test: Questionnaire renders all 18 questions from `GET /api/risk-profiler/questions`; each question shows options as radio buttons; cannot submit without answering all questions; after submission: SEBI riskometer visual shows correct category (Conservative=green zone, Aggressive=red zone); score meter animates to correct position; "Generate Compliance Pack" button disabled until `advisor_rationale` textarea has ≥ 50 characters; clicking "Generate Compliance Pack" calls `POST /api/pdf/compliance-pack` and downloads PDF
  3. Implement: Create `src/components/RiskProfiler/Questionnaire.tsx` (step-by-step or single-page form with React Hook Form); `src/components/RiskProfiler/ScoreMeter.tsx` (SEBI riskometer graphic as SVG arc with animated needle using Recharts or custom SVG); `src/components/RiskProfiler/CompliancePack.tsx` (rationale textarea + PDF download trigger); validation: all 18 questions required; rationale ≥ 50 chars
  4. Validate: RTL: incomplete questionnaire shows validation error; complete submission shows riskometer; Conservative answers → needle in green zone; Aggressive answers → needle in red zone; short rationale blocks PDF generation; full rationale triggers PDF download
  5. Success:
    - [x]Questionnaire captures all 18 questions (all SEBI-required dimensions) `[ref: PRD/Feature 6 AC]`
    - [x]Riskometer displays correct risk category visually `[ref: PRD/Feature 6 AC; risk category communication]`
    - [x]Compliance pack generation blocked without advisor rationale `[ref: PRD/Feature 6 AC; compliance pack]`

- [x] **T8.3 Scenario planner — SIP modeler** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `[ref: PRD/Should Have Features; Scenario Planner; SIP modeler]`
  2. Test: SIP Modeler renders 4 inputs: monthly SIP amount, expected return %, duration (years), annual step-up %; output shows: projected corpus, total invested, total gains; changing any input updates output instantly (client-side, no API call); "What if markets return 8% vs 12%?" dual-scenario comparison line chart shows both lines; SIP values formatted as Rs/Lakh/Crore appropriately
  3. Implement: Create `src/components/ScenarioPlanner/SIPModeler.tsx` with Recharts LineChart showing growth over time for two return scenarios; client-side future value calculation (no API); currency formatter (`src/utils/formatCurrency.ts` — Rs format with lakh/crore threshold)
  4. Validate: RTL: change return rate → chart updates instantly; 12% line always above 8% line; 30-year projection shows correct corpus vs known financial calculator
  5. Success: SIP scenario updates render in < 500ms (client-side calculation) `[ref: PRD/Should Have Features; Scenario Planner]`

- [x] **T8.4 Scenario planner — Portfolio stress test** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `[ref: PRD/Should Have Features; Portfolio Stress Test]` — COVID 2020, 2008, 2022 scenarios; and `[ref: SDD/Data Storage Schema; data/reference/stress_scenarios.json]`
  2. Test: Stress test panel shows 3 scenario cards; each card shows: scenario name, estimated portfolio drawdown % for selected asset class mix, historical recovery period (months); changing asset mix (equity %, debt %, gold %) updates estimated drawdown instantly; estimated drawdown for 100% equity portfolio in COVID 2020 = -38%; recovery bar chart shows months to recovery for each scenario
  3. Implement: Add `GET /api/scenarios/stress-test` endpoint (serves `stress_scenarios.json`); create `src/components/ScenarioPlanner/StressTest.tsx` with 3 scenario cards; drawdown formula: `weighted_drawdown = Σ(asset_weight × scenario_drawdown_for_asset)`; asset mix sliders total to 100%
  4. Validate: RTL: 3 scenario cards render; 100% equity → -38% for COVID 2020; mix of equity + debt → lower drawdown than pure equity; recovery periods shown correctly
  5. Success: Stress test shows correct drawdown for 3 historical scenarios based on selected asset mix `[ref: PRD/Should Have Features; Portfolio Stress Test]`

- [x] **T8.5 Scenario planner — Retirement withdrawal simulator** `[activity: frontend-ui]` `[parallel: true]`

  1. Prime: Read `[ref: PRD/Should Have Features; Scenario Planner; Retirement withdrawal simulator]`
  2. Test: Input: corpus amount (Rs), monthly withdrawal (Rs), expected return on remaining corpus (%); output: projected years corpus lasts as a line chart showing remaining balance over time; increasing return rate extends corpus life; corpus reaching zero shows "Corpus exhausted in X years" label; minimum corpus of Rs 10L enforced (validation)
  3. Implement: Create `src/components/ScenarioPlanner/RetirementWithdrawal.tsx`; client-side withdrawal simulation loop: each month subtract withdrawal, add growth on remaining, plot balance; Recharts AreaChart with zero-line annotation
  4. Validate: RTL: Rs 1 crore corpus, Rs 50K/month withdrawal, 8% return → last ~35+ years; 10% return → last even longer; Rs 1L/month → exhausts faster
  5. Success: Withdrawal simulator shows how long corpus lasts under different return and withdrawal assumptions `[ref: PRD/Should Have Features; Scenario Planner]`

- [x] **T8.6 Phase 8 Validation** `[activity: validate]`

  - Run full frontend test suite. Manual walkthrough: create goal → see projection → adjust step-up → see chart update; complete risk questionnaire → see riskometer → enter rationale → download compliance PDF; run SIP modeler with 2 scenarios; run stress test with 50% equity mix; run withdrawal simulator. All interactions complete without errors.

---

**Phase 8 Exit Criteria**: Goal planner creates goals and shows projections; risk profiler completes with riskometer and compliance PDF; all 3 scenario planner tools work client-side; full PRD Features 5-6 and Should-Have scenarios met.
