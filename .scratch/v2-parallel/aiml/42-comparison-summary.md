# 42: Comparison summary (stretch)

**What to build:** `explain_comparison` writes a short paragraph on which Business Archetype suits the Entrepreneur, using only namespaced placeholders (`dairy.min_dscr`), verified like the Entrepreneur View.

**Owner:** AIML

**Blocked by:** None (stretch; pick up only when your core tickets are done). Uses the client from 05.

**Status:** done

## Acceptance criteria

- [x] In replay mode, the summary passes `verify` against the merged, namespaced figures of 2 results.

## Comments

- Commit: `V2-42: Comparison summary test` (see `git log`).
- `explain_comparison` already existed from ticket 05. Added `tests/llm/test_comparison.py`: two real engine results, a scripted reply, summary verified against the namespaced merged figures (digit sentence stripped).
