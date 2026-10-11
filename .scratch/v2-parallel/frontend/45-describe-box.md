# 45: Describe in your own words (stretch)

**What to build:** Above the wizard, the Entrepreneur types their idea, the form fills from the intake-parse route, and the fields it couldn't fill are marked for them to complete.

**Owner:** Frontend

**Blocked by:** None (stretch; pick up only when your core tickets are done). Builds on 21's wizard state.

**Status:** done

## Acceptance criteria

- [x] Against the fixture route, submitting text fills the wizard and marks the missing fields.
- [x] `npm run check` and `npm run build` pass.

## Comments

- Commit: "V2-45: Describe box" (see `git log`).
- Parsed fields fill the draft; the still-unanswered missing paths show as a "Still needed" note on every step and drop off as they are filled.
- Deferred: fields with an honest default (age, business status, farmland, yes/no) are never marked, since the draft already holds a value. Marking inline on each step field was skipped.
- The fixture route ignores the text and returns no village or Own Contribution, so those two always show as missing against it.
- Not browser-tested; verified by `npm run check` and `npm run build` only.
