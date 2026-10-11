# 46: Compare page (stretch)

**What to build:** Compare takes the village and Own Contribution from the Entrepreneur's report or wizard draft. It shows metric rows with the better value marked by a check and the word "better", the summary paragraph, and a link to open a full DPR for each Business Archetype.

**Owner:** Frontend

**Blocked by:** None (stretch; pick up only when your core tickets are done). Reuses the renderer from 20.

**Status:** done

## Acceptance criteria

- [x] Against the fixture compare route, the rows and summary render with no `{{` at 360 px.
- [x] `npm run check` and `npm run build` pass.

## Comments

- Review: fixed refetch after an error with the same picks; skipped the other two findings (useLoad keys on a string, engine values are never NaN).
- Page reads `?report=<id>` (that report's input) or the complete wizard draft; otherwise shows an empty state. Picker: current locked, up to 2 others. "Open full DPR" posts a new intake for that Archetype at its default unit scale and opens the report.
- The fixture `/api/compare` returns identical numbers for every Archetype, so no "better" check shows against it; `betterIndex` is covered in `npm run check`.
- Deferred: nothing links to `/compare?report=<id>` yet (Report page "Compare with another business" button, wireframe 7); `ComparisonChart` is still a stub, so the DSCR bar chart is not drawn. `ChoiceCard` uses `role="radio"` for the multi-select picker.
