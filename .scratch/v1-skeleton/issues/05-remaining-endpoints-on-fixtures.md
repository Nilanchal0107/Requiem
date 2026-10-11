# 05: Remaining endpoints on fixtures

**What to build:** `simulate`, `compare`, `chat`, `intake/parse` and `voice/transcribe` respond with contract-shaped data. After this ticket all 16 endpoints respond and the API smoke test covers every one of them.

**V2 owner:** Fullstack (V1 is built by the single developer)

**Blocked by:** 02, 03

**Status:** done

## Notes

- `POST /api/simulate` returns the fixture `EngineResult`. It must not touch the DB or any LLM code.
- `POST /api/compare` returns one `EngineResult` per requested archetype id (the fixture result with `archetype_id` set), in request order, plus a summary paragraph whose placeholders use the `<archetype_id>.<figure_id>` form. An unknown archetype id is a 400.
- `POST /api/chat` returns a canned `ChatResponse` with one citation, one suggested change and `tools_used`. An unknown `report_id` is a 404.
- `POST /api/intake/parse` returns a canned partial `IntakeInput` and a `missing` list.
- `POST /api/voice/transcribe` accepts multipart audio and returns canned text. It is a stretch feature, so keep it to the declared shape.
- Each handler is a thin wrapper that V2 and V3 swap for the real engine and LLM calls. Keep the fixture access behind the loader from ticket 03 so the swap is one line per route.

## Acceptance criteria

- [x] All five endpoints return responses that validate against their contract models.
- [x] Compare returns the right number of results in order; unknown archetype → 400; one or four archetypes → 422.
- [x] Chat with an unknown report id returns 404.
- [x] `tests/test_api_smoke.py` now has at least one contract-validating test for **each of the 16 endpoints**, and `uv run pytest tests/test_api_smoke.py` passes.
- [x] Nothing in these routes imports `engine` or `llm`.

## Comments

- Done in the commit that carries this ticket update (hash in `git log`). `tests/test_api_smoke.py`: 9 new tests (29 in the file), full suite 44 passing (was 34). Pyright on the changed modules: 0 errors.
- **Shortcuts (each route is one fixture read, V2 swaps the body):**
  - `simulate` returns the `engine` block of `fixture/report.json` whatever the intake.
  - `compare` gives each archetype the fixture engine with `archetype_id` set. It does not apply each archetype's `unit_scale_default`, and the summary is English whatever `input.language` says.
  - `chat` answers only for the fixture report id `demo-niphad-dairy`; any other id is 404. `GET /api/reports/{id}` still serves the fixture under any id, so the two routes disagree on unknown ids until V2 reads the DB.
  - `intake/parse` ignores the text and returns the fixture's `archetype_id` and `unit_scale`.
  - `voice/transcribe` discards the audio and returns one canned sentence.
- **Hand-off for the frontend:** compare placeholders are `{{<archetype_id>.<figure_id>}}` as the contract says. The web resolves the prefix against `results[i].figures` where `archetype_id` matches. The summary is not yet in the figure registry, so the frontend must split on the first dot.
- **Coverage:** the smoke file now hits all 16 endpoints with contract models.
- **Contract:** no model changed, so `api/contracts.py` and `web/src/types/contracts.ts` are untouched.
- **Env:** `uv sync` was needed so `python-multipart` is in `.venv`; the voice route fails at import without it.
