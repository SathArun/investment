---
title: "Phase 6: PDF Generation Service"
status: completed
version: "1.0"
phase: 6
---

# Phase 6: PDF Generation Service

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/Internal API Changes; POST /api/pdf/client-report, POST /api/pdf/compliance-pack]`
- `[ref: SDD/Application Data Models; (PDF generation described in service layer)]`
- `[ref: PRD/Feature 4 Client Presentation Mode AC]` — PDF content requirements
- `[ref: PRD/Feature 6 SEBI Risk Profiling AC]` — Compliance pack content requirements
- `[ref: SDD/ADR-4; ReportLab PDF]` — ReportLab over WeasyPrint; charts as matplotlib PNGs

**Key Decisions**:
- ADR-4: ReportLab (pure Python); charts rendered by matplotlib, embedded as PNG in PDF
- All generated PDFs include SEBI mandatory disclaimer automatically — not optional
- Client report PDF must NOT contain Sharpe ratios or numerical sub-scores
- Advisor branding (logo, color, firm name) applied from `advisors` table

**Dependencies**:
- Phase 1 complete (DB; advisor branding fields in `advisors` table)
- Phase 4 complete (ProductRow data structure for client report)
- Phase 5 complete (risk_profiles data for compliance pack)

---

## Tasks

Implements both PDF generation flows: the branded client presentation report and the SEBI compliance pack for risk profiling documentation.

- [x] **T6.1 PDF layout engine + branding** `[activity: backend-pdf]`

  1. Prime: Read `[ref: SDD/ADR-4; ReportLab]` and `[ref: PRD/Feature 4 AC; PDF contains advisor logo, date, SEBI disclaimer]`
  2. Test: `build_branded_header(advisor)` returns a ReportLab Flowable with advisor's firm name, phone number, and logo image (if `logo_path` set); without logo, renders firm name in styled text; `build_sebi_disclaimer()` returns a Flowable containing exactly the string "Investment in securities market are subject to market risks. Read all the related documents carefully before investing."; disclaimer text is non-removable (called unconditionally in all PDF builds)
  3. Implement: Create `app/pdf/generator.py` with: `AdvisorBranding` dataclass loading from `advisors` table, `build_branded_header(branding)`, `build_sebi_disclaimer()`, `build_comparison_table(products, client_view=True)` (ReportLab Table with risk labels, returns, no Sharpe in client mode), `build_chart_png(chart_type, data)` (matplotlib figure → BytesIO PNG → ReportLab Image)
  4. Validate: Generate a test PDF with known branding; open PDF and verify firm name appears in header; verify SEBI disclaimer text is verbatim; verify table has no "Sharpe" column when `client_view=True`; verify logo renders without error when logo file is a 200×50px PNG
  5. Success:
    - [x] SEBI disclaimer present verbatim in every generated PDF `[ref: PRD/Should Have Features; SEBI Disclaimer Auto-Injection]`
    - [x] Advisor logo and firm name rendered in PDF header `[ref: PRD/Could Have Features; Branding Customization]`
    - [x] Client report PDF contains no Sharpe ratios or numerical sub-scores `[ref: PRD/Feature 4 AC]`

- [x] **T6.2 Client presentation report PDF** `[activity: backend-pdf]`

  1. Prime: Read `[ref: SDD/Internal API Changes; POST /api/pdf/client-report]` request/response schema and `[ref: PRD/Feature 4 AC; PDF contents]`
  2. Test: `POST /api/pdf/client-report {client_id, product_ids: [3 ids], tax_bracket: 0.30}` returns 200 with `Content-Type: application/pdf`; PDF binary is valid (starts with `%PDF`); PDF contains: advisor's firm name, today's date, client name, comparison table (3 rows × columns: product name, risk label, 1Y/3Y/5Y post-tax returns), SEBI disclaimer; unknown `product_id` in list returns 400; `product_ids` > 5 returns 422; PDF generates in < 10 seconds
  3. Implement: Create `app/pdf/templates/client_report.py` composing: branded header, optional summary section, comparison table (plain-language risk labels, no Sharpe/sub-scores), a 2-line editable "Advisor Notes" area, SEBI disclaimer footer; register `POST /api/pdf/client-report` in `app/pdf/router.py`
  4. Validate: Integration test generates PDF for 3 seeded products; PDF binary validates with PyPDF2; assert page count ≥ 1; assert SEBI disclaimer on every page; time assertion: generation < 10s; test with 5 products (max)
  5. Success:
    - [x] PDF generated in < 10 seconds for up to 5 products `[ref: SDD/Quality Requirements; Performance]`
    - [x] PDF binary starts with `%PDF-` (valid PDF) and is openable `[ref: SDD/Acceptance Criteria; PDF generation]`
    - [x] WhatsApp share link constructed correctly: `https://wa.me/?text=...` with PDF download URL `[ref: SDD/ADR-5]`

- [x] **T6.3 SEBI compliance pack PDF** `[activity: backend-pdf]`

  1. Prime: Read `[ref: SDD/Internal API Changes; POST /api/pdf/compliance-pack]` and `[ref: PRD/Feature 6 AC; compliance pack contents]`
  2. Test: `POST /api/pdf/compliance-pack {risk_profile_id}` returns PDF containing: client name and date, all 18 questionnaire questions and selected answers, calculated risk score (numeric), assigned risk category (text), risk category plain-language description, advisor's typed rationale (from `risk_profiles.advisor_rationale`), timestamp in DD-Mon-YYYY format, `retention_until` date; compliance pack for a profile with empty `advisor_rationale` field returns 422 (rationale required); PDF does NOT contain advisor's internal scoring algorithm weights
  3. Implement: Create `app/pdf/templates/compliance_pack.py` composing: client + advisor header, Q&A table (all questions and answers), scoring summary box (raw score, category, category description), advisor rationale section (bordered box with typed rationale text), timestamp + retention date footer, SEBI disclaimer, acknowledgment lines ("Advisor signature / date", "Client signature / date"); store PDF path in `risk_profiles.compliance_pdf_path`
  4. Validate: Integration test: create risk profile → generate compliance pack → assert all 18 Q&A pairs present; assert retention_until date = completed_at + 5Y; assert advisor rationale text appears verbatim; assert PDF generated in < 10s; assert compliance_pdf_path updated in DB after generation
  5. Success:
    - [x] All questionnaire Q&A pairs present in compliance pack `[ref: PRD/Feature 6 AC; compliance pack contents]`
    - [x] `compliance_pdf_path` updated in `risk_profiles` after generation `[ref: SDD/Acceptance Criteria; compliance pack stored]`
    - [x] Empty `advisor_rationale` blocked at API level (422) — cannot generate incomplete compliance docs `[ref: PRD/Feature 6 AC]`

- [x] **T6.4 Phase 6 Validation** `[activity: validate]`

  - Run `pytest tests/integration/test_pdf_generation.py`. Generate both PDF types and open in PDF viewer manually. Verify SEBI disclaimer verbatim in both. Verify no Sharpe/sub-scores in client report. Verify all Q&A in compliance pack. Measure generation time for 5-product report.

---

**Phase 6 Exit Criteria**: Both PDF types generate correctly; SEBI disclaimer in every PDF; client report has no advisor-internal metrics; compliance pack has all questionnaire Q&A; generation < 10s; compliance_pdf_path stored in DB.
