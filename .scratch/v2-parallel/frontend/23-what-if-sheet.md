# 23: What-if sheet

**What to build:** From the report, Try changes opens a sheet with sliders and − / + buttons for Own Contribution, business size and tenure. Results update through simulate as values change. A change that switches the Scheme or the Verdict is called out. The sheet has Reset, and "Make this a new DPR" creates a new report without touching the original. A Path to Yes Try button opens the sheet with that change applied.

**Owner:** Frontend

**Blocked by:** 20

**Status:** done

## Notes

- Implement the simulate hook. Simulate returns the fixture result until V3, so test that the call is made and the result is rendered, not that the numbers change.
- Bottom sheet on mobile, side panel on desktop.

## Acceptance criteria

- [x] Changing a value calls simulate with the changed intake and re-renders the key Figures.
- [x] Reset restores the original values.
- [x] "Make this a new DPR" creates a new report id, and the original report is unchanged.
- [x] `npm run check` and `npm run build` pass.

## Comments

- Commit: see `V2-23` in git log.
- `useSimulate` POSTs to `/api/simulate` (checked with a fake fetch). `whatChanged` in `lib/verdict.ts` flags a switched best Scheme or Verdict level; both are unit-checked in `plumbing.check.ts`. `NumberStepper` (− / +, optional `format`) was a stub and is now real.
- The sheet remounts its body on every open, so it always starts from the report's own values, or from the Path to Yes change when opened with **Try it**. Calls are debounced 300 ms and tagged with the intake, so a late answer never overwrites a newer one. While the answer is pending the previous result shows dimmed and "Make this a new DPR" is disabled.
- "Make this a new DPR" reuses `useReportStream().start` with `{...input, ...values}`, then navigates to the new report. It never writes to the original.
- Slider ranges: size from the archetype (`unit_scale_min/max/step`, loaded from `GET /api/archetypes`); Own Contribution 0 to project cost in ₹10,000 steps; tenure 12 to 84 months in steps of 6. Tenure is sent as `null` until moved.
- **Not verified in a browser**: the sheet, its layout at 360 px and the side panel from `sm` up were type-checked and built, not seen. No component test runner exists, so "re-renders the key Figures" and "Reset restores" are by construction (state in one component), not asserted.
- hi/mr strings in `report.json` are machine-assisted and need native review.
