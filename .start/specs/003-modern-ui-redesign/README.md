# Specification: 003-modern-ui-redesign

## Status

| Field | Value |
|-------|-------|
| **Created** | 2026-03-08 |
| **Current Phase** | Ready |
| **Last Updated** | 2026-03-08 |

## Documents

| Document | Status | Notes |
|----------|--------|-------|
| requirements.md | completed | 4 must-have features, 16 acceptance criteria |
| solution.md | completed | 4 ADRs confirmed, Flexbox shell, uiStore extended, CLIENT_VIEW_COLUMNS allowlist |
| plan/ | completed | 5 phases, 21 tasks, 3 parallel opportunities |

**Status values**: `pending` | `in_progress` | `completed` | `skipped`

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-08 | Approach: Sidebar + shadcn/ui Refresh | Biggest UX impact, reuses existing Radix + Tailwind + CVA stack, incremental migration |
| 2026-03-08 | PRD complete — 4 must-haves, 3 open questions | Dual-audience view switch is the anchor feature; skeleton loaders and hero cards are must-haves |
| 2026-03-08 | SDD complete — 4 ADRs confirmed | Flexbox shell, Zustand uiStore, coexistence token strategy, allowlist column approach |
| 2026-03-08 | Scope: Visual aesthetics + UX patterns (A & B) | User confirmed — not component architecture refactor |
| 2026-03-08 | Audience: Dual (advisor dense + client clean) | Presentation layer split only, no new routes |
| 2026-03-08 | Motion: Tailwind transitions only, no Framer Motion | Keep bundle lean, avoid new dependency |

## Context

Design approved in brainstorm session. See `.start/ideas/2026-03-08-modern-ui.md` for full design notes.

**Summary:** Replace top navbar with collapsible dark sidebar. Adopt shadcn/ui components on existing Radix + Tailwind stack. Inter font. Advisor view stays dense; client view auto-collapses sidebar and simplifies table. Skeleton loaders and Tailwind-only micro-interactions.

---
*This file is managed by the specify-meta skill.*
