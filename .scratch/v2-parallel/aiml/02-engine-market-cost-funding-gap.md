# 02: Engine: market, Project Cost and Funding Gap

**What to build:** The first half of the engine. Given the demo persona (dairy, Lasalgaon, ₹1 lakh Own Contribution), the engine produces the Locality market analysis, the Project Cost with working capital, and the Funding Gap. Every number is registered as a Figure with its Source Badge, formula and inputs.

**Owner:** AIML

**Blocked by:** 01

**Status:** ready-for-agent

## Notes

- Implement the figure registry, market, cost and means of finance (all except subsidy, which depends on the Scheme) to `docs/trd.md` §5.
- Figure ids follow the spec's grammar and keep the fixture report's ids (`households`, `market_gap`, `cost.animals`, `project_cost`, `funding_gap`, …). New ids are fine, renames are not. List any added ids in this ticket's comment.
- The engine stays pure: it does no I/O, and `current_year` is passed in. Every function keeps at least one `assert` check.
- Market mode: Aggregator Archetypes skip the Market Gap signal, and local Archetypes compute it.

## Acceptance criteria

- [ ] The registry rejects a duplicate Figure id.
- [ ] A test checks the dairy Project Cost and Funding Gap against hand-worked values.
- [ ] A test shows dairy (Aggregator) has no Market Gap signal and kirana (local) has one.
- [ ] Every money Figure is a whole number of rupees.
- [ ] `uv run pytest tests/engine` passes.
