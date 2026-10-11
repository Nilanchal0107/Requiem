# 12: New page shell and stream

**What to build:** The `/new` route with its wizard files declared and one working path through the whole pipeline: a "Start" button posts a canned intake, opens the SSE stream, shows each stage event as it arrives, and navigates to the report when `done` arrives. This proves the SSE contract end to end before any real wizard exists.

**V2 owner:** Frontend (V1 is built by the single developer)

**Blocked by:** 04, 10

**Status:** done

## Notes

- One file per wizard piece in a `new` folder: the "describe in your own words" box, the four steps (Where, Business, Money, About you). Each is declared with props and an empty body, and the page mounts them behind a stepper placeholder. V2 builds each independently.
- The Start button uses a canned `IntakeInput` built from fixture ids (a Niphad village, dairy, ₹1,00,000, the demo persona). Keep it in one file named as fixture-only so V2 can delete it.
- Implement `useReportStream` for real: create the report, open an `EventSource` on the stream, expose the list of stage events, the `done` state and an error. The StageTrace component is still a stub, so the page renders the events as a plain list of `stage: status`.
- Navigate to `/reports/:id` shortly after `done`. Stream errors show plain text with a retry.
- Add `en` keys to the wizard namespace only.

## Acceptance criteria

- [x] `/new` renders the four step components and the describe box (as stubs).
- [x] Pressing Start shows the six stages appearing in order with their statuses, then lands on `/reports/<id>`.
- [x] A closed or failed stream shows an error message and a retry button.
- [x] The hook has no knowledge of the page; the page owns navigation.
- [x] Only the wizard i18n namespace and files under the `new` folder, plus `useReportStream`, were added. (Also touched: `pages/NewReport.tsx`, which the page criteria require, and `checks/plumbing.check.ts`, which holds the new asserts.)
- [x] `npm run build` passes.

## Comments

- **Code commit:** see the `V1-12` commit on `main` (hash recorded in the next docs commit).
- **Verified:** `npm run build` passes. `npm run check` passes, including new asserts for `createReport` and `openReportStream` against a fake `EventSource` (stage order, `done` closes the stream, `onerror` fires the failure callback). Browser run through the Vite proxy with the real API: Start posts, the stages stream in order, the app lands on `/reports/<id>`. With the API stopped, Start shows the error text and a "Try again" button.
- **Not verified in a browser:** a full screenshot of all six stages at once (the run was captured mid-stream and then the URL change was checked). The stream-failure path (connection lost mid-stream) is covered by the fake-EventSource assert, not by a real dropped connection.
- **Deviations:**
  - The step and describe stubs take no props. The ticket asked for props, but no wizard state exists yet, so inventing a prop shape would be guessing. V2 adds the props with the real state.
  - `useReportStream` returns `{ start, events, reportId, failed }`. `start(intake)` posts the intake, then opens the stream. The two halves are exported as `createReport` and `openReportStream` so the check can test them without React.
  - The page navigates 600 ms after `done` so the last stage stays visible.
  - The canned intake uses `language: "en"`, while the fixture is `mr`, because the wizard namespace is `en` only.
- **For V2:** delete `web/src/pages/new/canned-intake.ts` when the wizard posts real state. Replace `StageTrace` in place of the plain `stage: status` list. Only `en` keys were added to `wizard.json`; `hi` and `mr` fall back to `en`.
