# 07: LLM declarations

**What to build:** The `llm/` package with every function declared and nothing implemented, plus one empty prompt file per prompt and the verifier's test cases written as named, skipped tests. After this ticket V2 fills in one file per task.

**V2 owner:** AIML (V1 is built by the single developer)

**Blocked by:** 01

**Status:** done

## Notes

- One file per area, matching `docs/architecture.md` §3 and `docs/trd.md` §6: client (provider switch, fallback), cache (`live | record | replay`), explain (Entrepreneur View and Comparison paragraph), verifier, intake parser, retrieval (BM25), chat (tool loop with `get_dpr`, `search_schemes`, `simulate`), eval.
- Signatures are the V2 seams, so settle them here with care. Use the contract models (`Explanation`, `ChatResponse`, `Figure`, `IntakeInput`…) for inputs and outputs. The verifier takes text plus the figures dict and returns what the explain step needs (verified count, total, offending sentences); its exact result type is your decision.
- One empty prompt template per use under a prompts folder, so prompts never conflict.
- `llm` may import `api.contracts` and `engine` only. It never touches the DB.
- The verifier's test file lists the seam-3 cases from the spec as named tests marked skipped with reason "V2": accepts valid placeholders, rejects ASCII digits, rejects Devanagari digits, rejects unknown ids, resolves namespaced Comparison ids.
- Every stub raises `NotImplementedError`. No real provider call, no key needed.

## Acceptance criteria

- [x] The package imports cleanly with no `.env` and no network, and imports nothing from the DB or the API routers.
- [x] Every function named in `docs/trd.md` §6 has a declared home with type hints and a docstring (what it takes, returns, and which TRD subsection defines it).
- [x] The cache module declares the three modes as a closed set of values.
- [x] One prompt file exists for each of: Entrepreneur View, Comparison paragraph, intake parsing, chat system prompt.
- [x] `uv run pytest tests/test_verifier.py` reports the five cases as skipped, not failed.
- [x] No two modules need to be edited together to implement one of them.

## Comments

- Done in `50422c9` (declarations, `tests/llm/test_declarations.py`, `tests/test_verifier.py`) and `0c40072` (TRD subsection cites in docstrings). Full suite: 68 passed, 5 skipped. `mypy llm` clean (ad hoc `uv run --with mypy`; mypy is not a project dependency).
- **Code review did not run.** The `code-review` skill returned an empty result. I reviewed the docstrings against the acceptance criteria by hand and fixed the gaps. Re-run the review before V2 relies on these seams.
- **Seam decisions taken here (V2 may revisit):**
  - `verify` returns `VerifyResult(verified, offending)`. `total` is derived by the caller as verified plus stripped sentences, because stripping happens after regeneration.
  - `SchemeIndex(texts_dir, source_urls)`: the caller passes `source_urls`, since `llm` may not import `data`.
  - `chat(..., what_if=...)`: `api/` injects a callable that runs `run_engine`, so `llm` never loads the catalogue. `tool_search_schemes` was dropped: the tool is `SchemeIndex.search`.
  - `complete` returns the raw `ChatCompletion`. `complete_json` returns a validated model.
- **Open for V2 (not decided):** `llm.eval.main()` needs the catalogue and village rows. `llm` may import neither `data` nor the DB, and `villages` lives in SQLite. Either `api/` or a `data/` script passes them in, or the eval reads JSON directly. Pick one before implementing `run_eval`.
- **New folder:** `tests/llm/` is outside the three listed test paths. It is AIML's, mirroring `tests/engine/`.
- **Test note:** the declaration test and the stubs landed in one commit. I did not observe a red run first.
