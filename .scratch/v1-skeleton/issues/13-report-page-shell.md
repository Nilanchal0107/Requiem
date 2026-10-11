# 13: Report page shell

**What to build:** `/reports/:id` loads the fixture report and renders a Verdict card above three tabs (Explanation, Numbers, Bank DPR). Each tab and each sheet is its own file, mounted and opening and closing from V1, with bodies left for V2. The result: two V2 developers can work on different tabs of the same page without ever editing the same file.

**V2 owner:** Frontend (V1 is built by the single developer)

**Blocked by:** 04, 10

**Status:** ready-for-agent

## Notes

- A thin report page owns fetching (`useReport`, implemented for real), the selected tab in the URL (`?tab=numbers`, default Explanation), and the open/closed state of the two sheets. It imports each piece by path; it contains no tab content.
- Files in a `report` folder: ReportHeader (wraps VerdictCard), ExplanationTab, NumbersTab, BankTab, WhatIfSheet, ChatSheet. Mount a BottomActionBar with "Try changes" and "Ask" buttons that toggle the sheets.
- **Shell content (proves the contract wiring, replaced in V2):**
  - header shows the verdict level and the matched scheme name as text
  - Explanation tab lists the section titles and raw text (placeholders unresolved)
  - Numbers tab lists the figure ids from `engine.figures`
  - Bank DPR tab lists the 12 section headings from `docs/prd.md` F5
  - the two sheets open to a labelled empty panel
- Show a skeleton-style "Loading…" and a plain error text with a retry on failure.
- Add `en` keys to the report and verdict namespaces only.

## Acceptance criteria

- [ ] `/reports/<any id>` renders the fixture report; `?tab=` switches tabs and survives reload and Back.
- [x] The header shows the Verdict level from the fixture.
- [ ] "Try changes" and "Ask" open and close their sheets; the sheets are in their own files.
- [x] Each tab, each sheet and the header is a separate file, and the page file contains no tab content.
- [ ] An API error shows a message and Retry.
- [x] `npm run build` passes.

## Comments

- **Code commit:** see the `V1-13` commit on `main` (hash recorded in the next docs commit).
- **Verified:** `npm run build` passes (`tsc -b` + `vite build`). `npm run check` passes with new asserts for `getReport` (URL) and `parseTab` (known tabs, unknown and missing values fall back to Explanation). The API serves `GET /api/reports/abc` as the fixture (verdict `feasible`, scheme MUDRA). In the browser, `?tab=numbers` shows the 26 figure ids and `?tab=bank` shows the 12 DPR headings; the header shows "Feasible" and "Scheme: MUDRA". "Try changes" opens its sheet with a title and an empty-state line.
- **Not verified in a browser (criteria left unticked):**
  - Closing the sheets, and "Ask" opening and closing. The renderer stopped answering screenshots right after "Ask" was clicked. This is probably a harness problem, but it is unconfirmed and needs a re-run.
  - Reload and Back keeping the `?tab=` state. The code uses `setSearchParams`, which pushes history, but this was not exercised.
  - The API-error path with Retry. It is implemented through `useReport` and `ErrorState`, but no failing request was run.
- **Deviations and additions:**
  - `ErrorState` and `BottomActionBar` had stub bodies that ignored their props, so the page could not show its error or its two buttons. Both bodies are now implemented. `ErrorState` takes a `retryLabel` prop, because the ticket limits new keys to the `report` and `verdict` namespaces.
  - Tab state is read with `parseTab` in `pages/report/tab.ts`, which is a pure helper so the check can cover it.
  - `ReportHeader` is a named export, matching the components folder. The sheets and tabs are named exports too. `Report.tsx` keeps its default export for the lazy router.
  - `report.engine` null (pending or failed report) shows `report.notReady` instead of crashing.
- **For V2:** `ExplanationTab` takes `explanation`, `NumbersTab` and `ReportHeader` take `engine`, and the two sheets take `open` and `onOpenChange`. Each file's body is the V2 surface; the page does not need to change to fill them in.
