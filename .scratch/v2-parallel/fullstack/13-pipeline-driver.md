# 13: Pipeline driver

**What to build:** `run_pipeline` is written and ready for V3. It runs the intake, market, cost, schemes, DPR and explanation stages as stage events, stores the engine result and explanation, and still completes the report, with the explanation marked unavailable, when the LLM fails.

**Owner:** Fullstack

**Blocked by:** 12

**Status:** done

## Notes

- It calls `run_engine` and `explain_report` once each, through their declared signatures (known conflict 5). Catalogues and the village come through the data loaders only.
- It isn't reachable while `USE_FIXTURES=1`, so V3 exercises it. Here it only has to import and type-check.

## Acceptance criteria

- [x] `run_pipeline` imports cleanly, with no remaining `NotImplementedError`.
- [x] The stage order matches the contract's stage list.
- [x] Read through the LLM-failure path: it yields an explanation-unavailable stage and still ends with done. Leave a note in the comment for V3 to test it.

## Comments

- Commit: see the commit that carries this ticket update ("V2-13: Pipeline driver").
- `run_pipeline` owns all persistence for its report: status `running` at start, each StageEvent appended to `report.stages` and committed as it's yielded, then `engine`, `explanation` and `done`. Engine or loader failure (unknown archetype or village included) yields a `failed` stage for the stage that broke, sets `failed`, and re-raises.
- LLM failure: `explain_report` raising, or returning `available=False`, yields `explanation`/`failed` ("Explanation unavailable, the numbers are complete") and still stores the report `done` with an empty unavailable Explanation. `regenerated=True` yields a `retrying` event before `done` (after the fact, `explain_report` has no progress hook).
- Already tested with stubbed loaders and engine in `tests/test_api_smoke.py` (LLM down, retry shown, engine failure). V3 should still run it once end to end with the real bodies and `LLM_MODE=replay`, plus once with the providers unreachable.
- Shortcut: `run_engine` is one call (known conflict 5), so `market` carries the whole engine duration and `cost`/`schemes`/`dpr` have `duration_ms: null`.
- A client disconnect mid-run (`GeneratorExit`, not caught by `except Exception`) leaves the report `running`. That's fine while the stream route re-runs anything not `done`: the pipeline resets `stages` on start. If V3 claims rows with `running` to block concurrent streams, it needs a staleness rule for this.
- Type-checked with `uv run --with mypy mypy api/pipeline.py` (no checker in `pyproject.toml`, which is frozen).
- **For V3 (swap in `api/reports.py`):** `_run_stages` body becomes `yield from run_pipeline(report_id, intake)`. `_play_and_store` must then stop writing `stages`/`engine`/`explanation`/`status` (the pipeline did) and only wrap the loop: stage events out, `except Exception` → `error` event with `{"detail": ...}`, else `done`. The stream route's session and the pipeline's own session both touch the row, so `session.refresh(row)` before any later read in the route.
