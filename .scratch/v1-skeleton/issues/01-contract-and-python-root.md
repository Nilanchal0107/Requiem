# 01: Contract and Python root

**What to build:** A Python project that installs with `uv sync` and starts with `uvicorn`, plus the frozen API contract. Every request and response model from `docs/api-contracts.md` §2–3 lives in `api/contracts.py`. Every endpoint is declared (path, method, request model, response model) in its own router module, with a handler that returns 501. The app includes all routers, so V2 never edits `main.py`. The TypeScript types are generated from the running app's OpenAPI schema.

**V2 owner:** Fullstack (V1 is built by the single developer)

**Blocked by:** None (can start immediately)

**Status:** done

## Notes

- Models not spelled out in the doc (`UserOut`, register/login request, `{report_id}` response, `{ok: true}`, `{user}` for `/me`, intake-parse request/response, compare request, transcribe response) must be defined too. Compare's `archetype_ids` is constrained to 2–3 items in the model, so a bad count is a 422.
- Router modules (one per group, so V2 never shares a file): auth, catalog, intake, reports, simulate, compare, chat, voice.
- `pyproject.toml` lists **every** Python dependency from `docs/trd.md` §1 up front: `fastapi`, `uvicorn[standard]`, `sqlmodel`, `itsdangerous`, `python-multipart`, `openai`, `rank-bm25`, `python-dotenv`, with `pytest` and `httpx` as dev dependencies. (`httpx` is required by FastAPI's `TestClient`, which the smoke tests use.) V2 must not edit `pyproject.toml` or `uv.lock`.
- `.env.example` holds every variable from `docs/trd.md` §3. `.python-version` pins 3.12.
- Create empty packages for `api/`, `engine/`, `llm/`, `data/` and the `tests/` folders so later tickets only add files.
- Generate the TS file with: `npx openapi-typescript http://localhost:8000/openapi.json -o web/src/types/contracts.ts`. Commit `contracts.py` and `contracts.ts` together.

## Acceptance criteria

- [x] `uv sync` succeeds on a clean checkout; `uv run uvicorn api.main:app` starts.
- [x] `/openapi.json` lists all 16 operations from `docs/prd.md` §8.1, each with the request and response models from the doc.
- [x] Every model in `docs/api-contracts.md` §2 exists in `contracts.py` with the same field names and types.
- [x] Every declared route returns 501 for now.
- [x] `web/src/types/contracts.ts` is generated, contains every model, and is never hand-edited.
- [x] `.env.example` is complete and `.env` stays git-ignored.
- [x] Money fields are `int`, rates are `float`, durations are months (per the conventions in the doc).

## Comments

- Done in `119714b`.
- Declared routes return 501 only once the request body validates; an empty body gives 422 (FastAPI default). Smoke tests in V2 must send valid bodies.
- `SESSION_SECRET` falls back to `change-me` in `api/main.py`; consider failing when unset. `load_dotenv()` in `api/main.py` runs after the router imports; move it above them if a module reads env at import time.
- `docs/prd.md` §8.1 lists `payload?` on `StageEvent`, but `api-contracts.md` does not; fix the PRD.
- `LoanTerms`, `RepaymentRow` and `YearProjection` use bare numbers rather than `Figure`; confirm with AIML before the freeze.
