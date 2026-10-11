# 11: Report persistence

**What to build:** Creating a report stores it with its intake and owner (none for a guest) under a new id. Getting it reads it back. Listing returns only the logged-in Entrepreneur's reports, newest first. A guest gets 401 on list, and an unknown id gets 404.

**Owner:** Fullstack

**Blocked by:** 10

**Status:** ready-for-agent

## Notes

- Until the stream finishes (ticket 12), a fresh report has no engine result. Get returns it as pending, as the contract describes.
- `USE_FIXTURES=1` stays on. Build test data inside the test file, and never edit fixtures.

## Acceptance criteria

- [ ] Create returns a new UUID each time, and the row stores the intake and the owner (or null).
- [ ] Get on an unknown id gets 404.
- [ ] List as a guest gets 401. Logged in, it shows only that Entrepreneur's reports, newest first.
- [ ] Every response validates against its contract model.
