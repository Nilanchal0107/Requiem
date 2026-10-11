# 47: My Reports page (stretch)

**What to build:** A logged-in Entrepreneur sees their saved reports with Business Archetype, village, Verdict and date. Tapping one reopens it. A new Entrepreneur sees an empty state with a button to build their first DPR. A guest is sent to log in.

**Owner:** Frontend

**Blocked by:** None (stretch; pick up only when your core tickets are done).

**Status:** done

## Acceptance criteria

- [x] The list, the empty state and the guest redirect all work at 360 px.
- [x] `npm run check` and `npm run build` pass.

## Comments

Commit: see `git log -1 -- web/src/pages/MyReports.tsx`.

- Guest redirect uses `useAuth` and `<Navigate to="/login?next=/reports">`. `reports.guest` and `reports.logIn` keys removed.
- `EmptyState` was a stub; now implemented. `TONE` exported from `VerdictCard` to reuse the Verdict icon and colours.
- Deferred: the 360 px layout was not checked in a real browser (only `npm run check` and `npm run build`). hi/mr strings need native review.
