---
title: "Content Area Dark Modernization — Implementation Plan"
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
- [x] Every test references SDD acceptance criteria
- [x] Integration tests in final phase
- [x] Project commands match actual setup

---

## Context Priming

*GATE: Read all files in this section before starting any implementation.*

**Specification**:
- `.start/specs/004-content-area-dark-modernization/solution.md` — Solution Design (ADRs, token map, implementation examples, gotchas)

**Key Design Decisions**:
- **ADR-1**: Dark class on `<html>` via `uiStore.isDarkMode` + root `useEffect` in `App.tsx`; `document.documentElement.classList.toggle('dark', isDarkMode)`
- **ADR-2**: Use semantic Tailwind tokens (`bg-card`, `bg-muted`, `text-foreground`, `text-muted-foreground`, `border-border`) — NOT hardcoded hex or CSS variable string literals (except Recharts SVG props: must use `hsl(var(--token))`)
- **ADR-3**: FilterBar raw `@radix-ui/react-select` → shadcn `Select` from `src/components/ui/select.tsx` — only JSX changes, all handlers preserved
- **ADR-4**: GoalForm two-column via `lg:grid lg:grid-cols-2 lg:gap-8` — CSS grid directly on outer div
- **ADR-5**: `isDarkMode` defaults to `true` (dark on first visit) — matches permanently-dark sidebar

**Implementation Context**:
```bash
# All commands run from: C:\Arun\investment\frontend

# Dev
npm run dev          # Vite on port 5173

# Quality (run after every task)
npm run typecheck    # TypeScript check
npm run lint         # ESLint

# Tests
npm test             # Vitest (watch mode)
npm run test -- --run  # Single pass

# Build
npm run build        # Production build
```

---

## Implementation Phases

- [x] [Phase 1: Foundation — uiStore, Dark Class, Layout](phase-1.md)
- [x] [Phase 2: Component Token Migrations](phase-2.md)
- [x] [Phase 3: Final Validation](phase-3.md)

---

## Plan Verification

| Criterion | Status |
|-----------|--------|
| Developer can follow without clarification | ✅ |
| Every task produces a verifiable deliverable | ✅ |
| All SDD acceptance criteria map to tasks | ✅ |
| All SDD components have implementation tasks | ✅ |
| Dependencies explicit, no circular refs | ✅ |
| Parallel opportunities marked | ✅ |
| Every task has spec references | ✅ |
| Project commands accurate | ✅ |
| All phase files exist and linked | ✅ |
