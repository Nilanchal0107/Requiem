# Fixtures

**Everything in this folder is illustrative.** The numbers, Scheme terms, Census figures and URLs are made up or copied for demo shape only. They are not verified data and must not be read as such.

- `localities.json`: Nashik district, Niphad block, three villages. Codes are fake (`FX…`) and household counts are placeholders.
- `archetypes.json`: the six Business Archetypes with unit-scale bounds and eligibility fields.
- `schemes.json`: the six Schemes. Only the PMEGP `source_url` comes from `docs/trd.md`. The other URLs are placeholders on `example.invalid`. Every `verified_on` is `1970-01-01`, so nobody mistakes these for checked figures.
- `report.json`: one complete Report for the demo persona (dairy, 5 animals, Pimpalgaon Baswant, ₹1,00,000 Own Contribution, language `mr`). Its figures are hand-built and internally consistent, but they are not engine output.
- `stage_events.json`: canned pipeline events for all six stages, each running then done.

These files are replaced from `data/` in V3. They are frozen after V1.
