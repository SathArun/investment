---
title: "Modern UI Redesign — Sidebar, shadcn/ui, Dual-Audience Views"
status: draft
version: "1.0"
---

# Implementation Plan

## Validation Checklist

### CRITICAL GATES (Must Pass)

- [x] All `[NEEDS CLARIFICATION]` markers addressed
- [x] All specification file paths correct and exist
- [x] Each phase follows TDD: Prime → Test → Implement → Validate
- [x] Every task has verifiable success criteria
- [x] A developer could follow this plan independently

### QUALITY CHECKS (Should Pass)

- [x] Context priming complete
- [x] All phases defined with linked phase files
- [x] Dependencies clear (no circular)
- [x] Parallel work tagged `[parallel: true]`
- [x] Activity hints provided
- [x] Every phase references relevant SDD sections
- [x] Every test references PRD acceptance criteria
- [x] Integration tests in final phase
- [x] Project commands match actual setup

---

## Context Priming

*GATE: Read all files in this section before starting any implementation.*

**Specification**:
- `.start/specs/003-modern-ui-redesign/requirements.md` — Product Requirements (personas, MoSCoW, acceptance criteria)
- `.start/specs/003-modern-ui-redesign/solution.md` — Solution Design (ADRs, directory map, implementation examples, gotchas)
- `.start/ideas/2026-03-08-modern-ui.md` — Approved design notes

**Key Design Decisions**:
- **ADR-1**: shadcn/ui coexistence — new components use CSS variables; existing keep Tailwind color classes; `--primary` overridden to blue-600 HSL `219 90% 56%`
- **ADR-2**: Flexbox app shell — `flex h-screen` with `transition-[width]` on sidebar (NOT `transition-all`)
- **ADR-3**: Zustand `uiStore` owns `isSidebarCollapsed` + localStorage persistence at key `sidebar_collapsed`
- **ADR-4**: `CLIENT_VIEW_COLUMNS` allowlist in AssetTable — columns hidden by default, explicitly opted-in

**Implementation Context**:
```bash
# All commands run from: C:\Arun\investment\frontend

# Dev
npm run dev          # Vite on port 5173+

# Quality (run after every task)
npm run typecheck    # TypeScript check
npm run lint         # ESLint

# Tests
npm test             # Vitest (watch mode)
npm run test -- --run  # Single pass

# Build
npm run build        # Production build

# shadcn/ui (one-time Phase 1)
npx shadcn@latest init
npx shadcn@latest add button input card badge select skeleton tooltip separator
```

---

## Implementation Phases

- [ ] [Phase 1: Foundation — shadcn/ui, Inter Font, uiStore](phase-1.md)
- [ ] [Phase 2: App Shell and Sidebar Navigation](phase-2.md)
- [ ] [Phase 3: Dual-Audience Dashboard — ViewToggle, FilterSummary, AssetTable, RiskReturnPlot](phase-3.md)
- [ ] [Phase 4: ProductPins Hero Cards and Skeleton Loaders](phase-4.md)
- [ ] [Phase 5: shadcn/ui Component Migration and Integration Tests](phase-5.md)

---

## Plan Verification

| Criterion | Status |
|-----------|--------|
| Developer can follow without clarification | ✅ |
| Every task produces a verifiable deliverable | ✅ |
| All PRD acceptance criteria map to tasks | ✅ |
| All SDD components have implementation tasks | ✅ |
| Dependencies explicit, no circular refs | ✅ |
| Parallel opportunities marked | ✅ |
| Every task has spec references | ✅ |
| Project commands accurate | ✅ |
| All phase files exist and linked | ✅ |
