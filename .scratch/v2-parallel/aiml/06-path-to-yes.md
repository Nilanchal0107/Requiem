# 06: Path to Yes

**What to build:** When the Verdict isn't Feasible, `run_engine` suggests the smallest change that reaches Feasible: more Own Contribution, a smaller start, or a longer tenure. The suggestion is checked by re-running the engine.

**Owner:** AIML

**Blocked by:** 03

**Status:** ready-for-agent

## Notes

- Path to Yes calls the engine again with Path to Yes disabled (the wiring is already in `run_engine`).
- Search within the Archetype's unit-scale bounds and the Scheme's maximum tenure only.
- If nothing reaches Feasible, `path_to_yes` stays null. The frontend already renders nothing in that case.

## Acceptance criteria

- [ ] For a non-Feasible case built in the test, the suggested change, re-run through `run_engine`, comes back Feasible.
- [ ] A Feasible input returns `path_to_yes` null.
- [ ] No suggestion goes outside the Archetype bounds or the Scheme's tenure limit.
