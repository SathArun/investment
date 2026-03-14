# Specification: 005-dark-mode-and-ingestion-fixes

## Status

| Field | Value |
|-------|-------|
| **Created** | 2026-03-14 |
| **Current Phase** | Ready |
| **Last Updated** | 2026-03-14 |

## Documents

| Document | Status | Notes |
|----------|--------|-------|
| requirements.md | completed | PRD authored 2026-03-14 |
| solution.md | completed | SDD approved 2026-03-14 — all 5 ADRs confirmed |
| plan/ | completed | 5-phase plan written 2026-03-14 |

**Status values**: `pending` | `in_progress` | `completed` | `skipped`

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-14 | Dark mode: token migration only (no new CSS) | 7 components use hardcoded light Tailwind classes; swap to semantic tokens is sufficient |
| 2026-03-14 | NPS: reverse-engineer underlying data endpoint | JS-rendered site confirmed broken; avoid heavy headless browser dependency |
| 2026-03-14 | AMFI + mfapi: replace with alternatives | Multiple fix attempts failed; replace rather than debug |
| 2026-03-14 | NPS fallback: static JSON seed if endpoint not found | NPS returns change weekly at most; static seed is acceptable if direct endpoint unavailable |

## Context

Two distinct issues bundled into one spec:
1. **UI Dark Mode Gaps** — 7 React components use hardcoded Tailwind light colors; breaks dark theme.
2. **Data Ingestion Failures** — AMFI, mfapi, and NPS scheduled jobs fail to return data consistently. NPS is confirmed broken by design (JS-rendered site). AMFI and mfapi need replacement with more reliable alternatives.

---
*This file is managed by the specify-meta skill.*
