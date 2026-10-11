# 12: Stream stores and replays stage events

**What to build:** Opening a report's stream plays the stage events and stores them on that report. It saves the result and explanation under the report's own id and marks it done. Opening the stream again replays the stored events without re-running anything. Get then returns the finished report under its own id.

**Owner:** Fullstack

**Blocked by:** 11

**Status:** done

## Notes

- With `USE_FIXTURES=1`, the events and result are the fixture's, but stored per report. Keep a `shortcut:` comment naming the `run_pipeline` call V3 swaps in.

## Acceptance criteria

- [x] Create, then stream: the stage events arrive in the contract's stage order and end with the done event.
- [x] Get after the stream returns the full report with the report's own id.
- [x] A second stream replays the stored events (same order and count) and doesn't re-run the stages.

## Comments

- Commit: `V2-12: Stream stores and replays stage events` (see git log).
- `_run_stages(report_id, intake)` in `api/reports.py` is the seam: its `shortcut:` comment says V3 swaps the body for `yield from run_pipeline(report_id, intake)`.
- For ticket 13 / V3: `_play_and_store` currently writes `stages`, `engine`, `explanation` and `status="done"` itself (engine and explanation are the fixture's). Ticket 13 says `run_pipeline` stores the engine result and explanation, so when V3 swaps it in, drop that write from `_play_and_store` to avoid storing twice. Keep the `stages` write and the `done` status here, or move them into `run_pipeline`. Pick one place.
- The stream uses the same access check as GET (`_readable_row`): an unknown id, or someone else's owned report, gets 404.
- A `done` report replays its stored events immediately (no delay), byte-identical to the first stream.
- `fixture("report.json")` loads before the response starts, so `USE_FIXTURES=0` gives a clean 501 rather than a broken stream.
- Deferred, marked `shortcut:`: no `error` event or `failed` status on engine failure (V3's `run_pipeline` adds both); two concurrent streams on a pending report both run, and the last write wins (claim the row with `running` if the live pipeline makes that costly).
- Also stale: the `api/pipeline.py` docstring says "implemented in V2" and `api/db.py` says "Nothing reads or writes them yet". I didn't change either.
