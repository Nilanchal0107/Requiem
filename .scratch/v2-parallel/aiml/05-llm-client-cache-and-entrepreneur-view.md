# 05: LLM client, cache and Entrepreneur View

**What to build:** Given an `EngineResult` and a language, `explain_report` returns a verified Entrepreneur View `Explanation` in English, Hindi or Marathi. It runs live against Gemini with Groq as fallback, and works offline in replay mode.

**Owner:** AIML

**Blocked by:** 04

**Status:** done

## Notes

- The client is OpenAI-compatible: Gemini first, Groq if Gemini fails. Keys come from `.env` only.
- The cache key is a hash of model, messages and tools. `LLM_MODE=live|record|replay`, and replay raises on a cache miss instead of calling out.
- The prompt gets Figure ids and units, never values.
- If verify fails, regenerate once. If it fails again, strip the failing sentences and report verified / total.
- Engine input for tests: build it inside the test, or use the fixture report's engine block. Don't wait for tickets 02 and 03.

## Acceptance criteria

- [x] In replay mode, with a committed cache file, `explain_report` returns a contract-valid `Explanation` with no digits and every placeholder resolving.
- [x] A replay-mode test with a cached bad reply (containing a digit) shows one regeneration, then sentence stripping and a verified count below the total.
- [x] A replay cache miss raises instead of calling the network.
- [ ] Record mode run once by hand for the demo persona in Marathi. The cache file is committed. *(manual step — `GEMINI_API_KEY=<key> LLM_MODE=record .venv/bin/python scripts/record_marathi_explanation.py`, then `git add data/llm_cache/<hash>.json`)*

## Comments

- Implemented `llm/cache.py` (`cache_key` — SHA-256 of model + messages + tools; `CacheMode` StrEnum `live|record|replay`).
- Implemented `llm/client.py` (`complete` with Gemini-primary/Groq-fallback, per-mode cache read/write; `complete_json` with one schema-error retry).
- Implemented `llm/prompts/entrepreneur_view.md` — system prompt that injects a figure table (ids + units, never values), abridged engine JSON (repayment and figures dict stripped), language, and verdict summary. Uses `{token}` replacement instead of `str.format()` to survive JSON curly braces in the payload.
- Implemented `llm/prompts/comparison.md` — namespaced placeholder format `{{archetype_id.figure_id}}`.
- Implemented `llm/explain.py`:
  - `explain_report`: builds system prompt → calls `complete(json=True)` → verifies all section texts and SWOT items → regenerates once on failure → strips remaining offending sentences → reports `verified/total/regenerated`. Returns `available=False` on total LLM failure.
  - `explain_comparison`: builds namespaced figure registry → renders comparison prompt → calls `complete` → strips offending sentences (single call, no regen).
- Added `tests/llm/test_explain.py` covering all three automated ACs (25 tests total, all pass).
