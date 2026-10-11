# 12: Stream stores and replays stage events

**What to build:** Opening a report's stream plays the stage events and stores them on that report. It saves the result and explanation under the report's own id and marks it done. Opening the stream again replays the stored events without re-running anything. Get then returns the finished report under its own id.

**Owner:** Fullstack

**Blocked by:** 11

**Status:** ready-for-agent

## Notes

- With `USE_FIXTURES=1`, the events and result are the fixture's, but stored per report. Keep a `shortcut:` comment naming the `run_pipeline` call V3 swaps in.

## Acceptance criteria

- [ ] Create, then stream: the stage events arrive in the contract's stage order and end with the done event.
- [ ] Get after the stream returns the full report with the report's own id.
- [ ] A second stream replays the stored events (same order and count) and doesn't re-run the stages.
