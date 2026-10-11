# 06: Path to Yes

**What to build:** When the Verdict isn't Feasible, `run_engine` suggests the smallest change that reaches Feasible: more Own Contribution, a smaller start, or a longer tenure. The suggestion is checked by re-running the engine.

**Owner:** AIML

**Blocked by:** 03

**Status:** done

## Notes

- Path to Yes calls the engine again with Path to Yes disabled (the wiring is already in `run_engine`).
- Search within the Archetype's unit-scale bounds and the Scheme's maximum tenure only.
- If nothing reaches Feasible, `path_to_yes` stays null. The frontend already renders nothing in that case.

## Acceptance criteria

- [x] For a non-Feasible case built in the test, the suggested change, re-run through `run_engine`, comes back Feasible.
- [x] A Feasible input returns `path_to_yes` null.
- [x] No suggestion goes outside the Archetype bounds or the Scheme's tenure limit.

## Comments

- Commit: `V2-06: Path to Yes` (see `git log`).
- `engine/path_to_yes.py`: Own Contribution up in ₹5,000 steps to Project Cost, unit scale down by the Archetype step to its min, tenure to the best Scheme's maximum. Each is a single change, first value that re-runs to `feasible`; `run_engine` already returns null for a Feasible input.
- `tests/engine/test_path_to_yes.py` sweeps villages × Archetypes × scale × Own Contribution, re-runs every suggestion through the engine and checks the bounds.
- Own Contribution is only searched upward from the current value; tenure is skipped when the best Scheme is already at its maximum.
