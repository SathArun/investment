---
title: "Phase 3: mfapi Backfill Hardening"
status: completed
version: "1.0"
phase: 3
---

# Phase 3: mfapi Backfill Hardening

## Phase Context

**GATE**: Read all referenced files before starting this phase.

**Specification References**:
- `[ref: SDD/mfapi Fix — Longer Backoff + Batch Cursor]` — constants, cursor functions, and `backfill_all_schemes()` changes
- `[ref: SDD/Runtime View — mfapi Backfill with Cursor]` — sequence diagram
- `[ref: PRD/Feature 3 — mfapi Historical Backfill]` — acceptance criteria

**Key Decisions**:
- ADR-4: File-based cursor at `backend/data/mfapi_cursor.txt`. Written after each scheme in the batch; cleared when all schemes processed.
- ADR-5: No shared retry utility — mfapi keeps per-scheme 429 backoff (now 120s).
- Batch cap: 500 schemes per run.
- Cursor comparison is string-based (scheme codes are stored as strings).

**Dependencies**:
- None. Independent of Phases 1, 2, and 4.

---

## Tasks

Delivers a mfapi backfill job that respects rate limits (120s 429 backoff), caps at 500 schemes per Sunday run, and resumes from a cursor on the next run — ensuring all schemes are eventually backfilled without the job running indefinitely.

---

- [ ] **T3.1 Add cursor helpers and increase 429 backoff** `[activity: backend-api]`

  1. **Prime**: Read `backend/app/jobs/ingest_mfapi.py`. Review SDD cursor spec `[ref: SDD/mfapi Fix — Longer Backoff + Batch Cursor]`.
  2. **Test**: Write/update tests asserting:
     - `read_cursor()` returns `None` when cursor file absent; returns the stored string when present.
     - `write_cursor("100026")` writes `"100026"` to `CURSOR_FILE`.
     - `clear_cursor()` deletes the file; is a no-op when file absent.
     - `RATE_LIMIT_BACKOFF_SECONDS` equals `120`.
  3. **Implement**:
     - Change `RATE_LIMIT_BACKOFF_SECONDS = 60` → `RATE_LIMIT_BACKOFF_SECONDS = 120`.
     - Add `BATCH_LIMIT = 500` constant.
     - Add `CURSOR_FILE = Path("data/mfapi_cursor.txt")`.
     - Implement `read_cursor() -> str | None`, `write_cursor(scheme_code: str) -> None`, `clear_cursor() -> None` (see SDD for exact logic).
  4. **Validate**: `pytest tests/ -k mfapi` passes for cursor helper tests.
  5. **Success**: Cursor file helpers work correctly; backoff constant is 120. `[ref: SDD/mfapi Fix]`

---

- [ ] **T3.2 Cursor-based batch cap in `backfill_all_schemes()`** `[activity: backend-api]`

  1. **Prime**: Re-read `backfill_all_schemes()` in `ingest_mfapi.py`. Review SDD sequence diagram `[ref: SDD/Runtime View — mfapi Backfill with Cursor]`.
  2. **Test**: Write/update tests asserting:
     - When cursor = `"100026"` and schemes = `["100020", "100026", "100030", "100040"]`, the function skips `"100020"` and `"100026"`, processes `"100030"` and `"100040"`.
     - When `BATCH_LIMIT` schemes are processed, the cursor is written with the last processed code and the function stops.
     - When all remaining schemes are processed within the cap, the cursor file is cleared.
     - When a scheme raises an exception, it is logged and skipped (existing behaviour preserved).
  3. **Implement**: Modify `backfill_all_schemes()`:
     - Call `read_cursor()` at the start; store as `last_cursor`.
     - Add `past_cursor = (last_cursor is None)` flag.
     - In the scheme loop: if `not past_cursor`, check if `fund.scheme_code == last_cursor`; if so, set `past_cursor = True` and `continue` (skip the cursor scheme itself since it was already processed).
     - Add `schemes_processed_this_run = 0` counter; increment after each successful scheme.
     - After processing each scheme, call `write_cursor(fund.scheme_code)`.
     - When `schemes_processed_this_run >= BATCH_LIMIT`, break the loop (cursor already written).
     - After the loop: if `past_cursor` is True and batch cap was NOT hit, call `clear_cursor()` (all done).
  4. **Validate**: `pytest tests/ -k mfapi` all pass. Run `python -m app.jobs.ingest_mfapi` — check that `data/mfapi_cursor.txt` is created and contains a scheme code after the run.
  5. **Success**:
     - Each run processes ≤500 schemes. `[ref: PRD/AC-3.1]`
     - Next run resumes from cursor, not from scratch. `[ref: PRD/AC-3.3]`
     - HTTP 429 triggers 120s backoff and retry. `[ref: PRD/AC-3.2]`

---

- [ ] **T3.3 Phase 3 Validation** `[activity: validate]`

  Run `pytest tests/ -k mfapi` from `backend/`. All must pass.

  Manual integration check:
  - [ ] `python -m app.jobs.ingest_mfapi` creates/updates `data/mfapi_cursor.txt`.
  - [ ] Re-running the job skips schemes up to the cursor, then processes the next batch.
  - [ ] After a full cycle (all schemes processed), cursor file is absent.

  Success: mfapi job runs ≤500 schemes per run and resumes from cursor on next invocation. `[ref: PRD/AC-3.1, AC-3.3]`
