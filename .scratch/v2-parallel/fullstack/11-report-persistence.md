# 11: Report persistence

**What to build:** Creating a report stores it with its intake and owner (none for a guest) under a new id. Getting it reads it back. Listing returns only the logged-in Entrepreneur's reports, newest first. A guest gets 401 on list, and an unknown id gets 404.

**Owner:** Fullstack

**Blocked by:** 10

**Status:** done

## Notes

- Until the stream finishes (ticket 12), a fresh report has no engine result. Get returns it as pending, as the contract describes.
- `USE_FIXTURES=1` stays on. Build test data inside the test file, and never edit fixtures.

## Acceptance criteria

- [x] Create returns a new UUID each time, and the row stores the intake and the owner (or null).
- [x] Get on an unknown id gets 404.
- [x] List as a guest gets 401. Logged in, it shows only that Entrepreneur's reports, newest first.
- [x] Every response validates against its contract model.

## Comments

- Commit: `V2-11: Report persistence` (see git log).
- `_to_contract(row)` in `api/reports.py` turns a `db.Report` row into the contract `Report`. Ticket 12 should reuse it.
- `_demo_report` is deleted. The stream still replays fixture events (ticket 12 stores them per report).
- Behaviour change for Frontend: between this commit and ticket 12, `GET /api/reports/{id}` returns `status: "pending"` with `engine`/`explanation` null, and the old "any id returns the fixture" behaviour is gone (unknown id → 404).
- `village_name` in the list comes from `fixtures/localities.json` (falls back to the code). `shortcut:` comment marks it; V3 reads names through the data loaders.
- GET access (review follow-up): a guest report (`owner_id` null) is readable by whoever holds its UUID. An owned report returns 404 to anyone but its owner, since it carries eligibility data. Ticket 12 should apply the same check to the stream.
