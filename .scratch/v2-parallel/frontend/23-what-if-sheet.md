# 23: What-if sheet

**What to build:** From the report, Try changes opens a sheet with sliders and − / + buttons for Own Contribution, business size and tenure. Results update through simulate as values change. A change that switches the Scheme or the Verdict is called out. The sheet has Reset, and "Make this a new DPR" creates a new report without touching the original. A Path to Yes Try button opens the sheet with that change applied.

**Owner:** Frontend

**Blocked by:** 20

**Status:** ready-for-agent

## Notes

- Implement the simulate hook. Simulate returns the fixture result until V3, so test that the call is made and the result is rendered, not that the numbers change.
- Bottom sheet on mobile, side panel on desktop.

## Acceptance criteria

- [ ] Changing a value calls simulate with the changed intake and re-renders the key Figures.
- [ ] Reset restores the original values.
- [ ] "Make this a new DPR" creates a new report id, and the original report is unchanged.
- [ ] `npm run check` and `npm run build` pass.
