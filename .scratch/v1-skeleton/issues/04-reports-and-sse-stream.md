# 04: Reports and SSE stream

**What to build:** The full report lifecycle on fixtures. Posting an intake returns a report id. The stream endpoint sends the canned stage events in order with a short delay between them and ends with `done`. Getting a report returns the fixture report under the requested id. Listing reports returns 401 for guests and one summary for a logged-in user. The real pipeline driver is declared and left for V2.

**V2 owner:** Fullstack (V1 is built by the single developer)

**Blocked by:** 02, 03

**Status:** done

## Notes

- `POST /api/reports` validates the `IntakeInput` and returns a new id. Nothing is persisted in V1, so every id resolves to the fixture report with `id` set to the requested value.
- The SSE format is in `docs/api-contracts.md` §3: `event: stage` per `StageEvent`, then `event: done` with `{"report_id": ...}`. Use `StreamingResponse` with `text/event-stream`.
- Declare the real pipeline generator in `api/pipeline.py` (signature only, `NotImplementedError`). The V1 route streams the fixture events through a separate small generator, which V3 deletes.
- The list route uses `require_user` from ticket 03.

## Acceptance criteria

- [x] `POST /api/reports` with a valid body returns `{report_id}`; an invalid body returns 422.
- [x] `GET /api/reports/{id}/stream` yields the 6 stages in order (`intake → market → cost → schemes → dpr → explanation`), each `running` then `done`, then a `done` event. A smoke test parses the stream and asserts the order.
- [x] `GET /api/reports/{id}` returns a contract-valid `Report`.
- [x] `GET /api/reports` returns 401 for a guest and a `ReportSummary[]` after login.
- [x] `run_pipeline` in `api/pipeline.py` is declared with its final signature and raises `NotImplementedError`.
- [x] Smoke tests for these four endpoints pass.

## Comments

- Built with tests first in `tests/test_api_smoke.py` (4 new tests plus the stream test, 19 in the file). Full suite 34 passing. Pyright on `api/reports.py` and `api/pipeline.py`: 0 errors. No project typechecker is configured; pyright was run ad hoc via `uvx` against `.venv`.
- **Code review (Standards and Spec, parallel sub-agents):** no hard violations; no missing or partial requirements. Applied: `_demo_report()` helper (dedupes the fixture load), `_replay` renamed `_replay_fixture_stages`, and a typing fix (`engine` is optional, so `verdict` is `None` when absent).
- **Deferred:** `list_reports` uses `next(...)` with no default, so an unknown village code gives a 500. Not reachable with the fixture; V2 reads the village from the DB. `_replay_fixture_stages` sleeps after the last event too, so `done` arrives about 0.25 s late. `run_pipeline` is a plain function that raises on call, not a generator; V2 makes it one. The mixed serialization (`model_dump_json` for stages, `json.dumps` for `done`) is kept.
- **Contract:** no model changed, so `api/contracts.py` and `web/src/types/contracts.ts` are untouched.
- **Notes for V2:** `run_pipeline(report_id, intake) -> Iterator[StageEvent]` is the final signature. Replace `_demo_report` and `_replay_fixture_stages` when the DB and pipeline land.
