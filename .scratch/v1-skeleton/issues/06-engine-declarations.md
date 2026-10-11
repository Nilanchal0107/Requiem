# 06: Engine declarations

**What to build:** The `engine/` package with every function declared and nothing implemented. After this ticket V2 can implement each module independently without creating or editing a shared file. `run_engine` already calls the modules in the right order, so wiring is done.

**V2 owner:** AIML (V1 is built by the single developer)

**Blocked by:** 01

**Status:** done

## Notes

- One file per area, matching `docs/architecture.md` §3: cost, market, schemes, finance, verdict, path to yes, and a figure registry. The package entry point exposes `run_engine(input, archetype, schemes, village, *, with_path_to_yes=True) -> EngineResult` and calls the module functions in the order in `docs/trd.md` §5.
- Function names and signatures are the V2 seams, so settle them here with care. They are a proposal until you accept them: take the formulas from `docs/trd.md` §5.1–5.9, and name inputs and outputs after the contract models.
- **Purity rules (ADR 0001, CLAUDE.md rule 2):** the engine imports only `api.contracts` and the standard library. The catalogue (archetype, schemes, village) arrives as plain dicts or contract models passed in by the caller; the engine never imports `data`, `llm`, the DB or anything doing I/O.
- Each stub's docstring states inputs, outputs, the TRD section it implements, and that V2 must add at least one `assert` check.
- The figure registry declares the "unique id" rule and `as_dict()` for `EngineResult.figures`, but implements nothing.
- Every stub raises `NotImplementedError`.

## Acceptance criteria

- [x] The package imports cleanly. A test imports every engine module and asserts none of `llm`, `data`, `sqlmodel`, `openai`, `httpx` or the API routers end up in `sys.modules` because of it.
- [x] Every function named in `docs/trd.md` §5 has a declared home with type hints and a docstring.
- [x] `run_engine` calls the module functions in the order of the report pipeline stages (market → cost → schemes → finance/projections → verdict → path to yes).
- [x] `run_engine` raises `NotImplementedError` coming from the first stub (not a wiring error).
- [x] No two modules need to be edited together to implement one of them (check: each V2 implementation task from the PRD maps to one file).

## Comments

- Done in `5597b0c` (engine + `tests/engine/test_declarations.py`). 10 tests pass; full suite 54 pass; mypy clean on `engine/`.
- **Signature change to confirm:** `run_engine` takes a required keyword-only `current_year` that the TRD §5 signature does not list. §5.2 needs the year and the engine must not read the clock. Accept it or name another way to pass the year.
- **Seams to settle in V2 (not decided here):**
  - `MarketAnalysis.market_gap` is a required `Figure`, but TRD §5.2 says aggregator mode produces none. Decide: optional field, or a zero figure with a note.
  - `min_dscr` has no value when there is no debt service (TRD §5.6 says `None`), and `Figure.value` is a required `float`. Decide the representation (contract change) before implementing.
  - `decide_verdict` and `break_even_month` have no defined result when no Scheme is eligible (no tenure, empty schedule).
  - `payback_months` returns `NOT_PAID_BACK = 999` as an ordinary value. Consider a flag or an explicit contract field, so the UI doesn't show "999 months".
  - `monthly_operating` returns whole rupees; the TRD does not say how fractional revenue is rounded.
- **Test gap:** `test_run_engine_stops_at_the_first_stub` stops at the first stub, so the wiring after it (`EngineResult(...)` keyword names, `best.terms`, `finance.subsidy`) runs only in V2. Those names match `api/contracts.py` by reading, not by a test.
- **CLAUDE.md rule 2 (every function has an `assert`):** stubs have none, deliberately; V2 must add one per function. This is the ticket's stated deferral, not an exception to the rule.
