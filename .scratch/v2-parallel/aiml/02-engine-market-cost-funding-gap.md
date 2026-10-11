# 02: Engine: market, Project Cost and Funding Gap

**What to build:** The first half of the engine. Given the demo persona (dairy, Lasalgaon, ₹1 lakh Own Contribution), the engine produces the Locality market analysis, the Project Cost with working capital, and the Funding Gap. Every number is registered as a Figure with its Source Badge, formula and inputs.

**Owner:** AIML

**Blocked by:** 01

**Status:** done

## Notes

- Implement the figure registry, market, cost and means of finance (all except subsidy, which depends on the Scheme) to `docs/trd.md` §5.
- Figure ids follow the spec's grammar and keep the fixture report's ids (`households`, `market_gap`, `cost.animals`, `project_cost`, `funding_gap`, …). New ids are fine, renames are not. List any added ids in this ticket's comment.
- The engine stays pure: it does no I/O, and `current_year` is passed in. Every function keeps at least one `assert` check.
- Market mode: Aggregator Archetypes skip the Market Gap signal, and local Archetypes compute it.

## Acceptance criteria

- [x] The registry rejects a duplicate Figure id.
- [x] A test checks the dairy Project Cost and Funding Gap against hand-worked values.
- [x] A test shows dairy (Aggregator) has no Market Gap signal and kirana (local) has one.
- [x] Every money Figure is a whole number of rupees.
- [x] `uv run pytest tests/engine` passes.

## Comments

- Implemented `engine/figures.py` (`FigureRegistry.add` with unique ID check and whole rupee verification for INR, `FigureRegistry.as_dict`).
- Implemented `engine/market.py` (`households_now`, `our_capacity`, `sales_ceiling`, `analyse_market` handling aggregator vs local modes).
- Implemented `engine/cost.py` (`build_cost` calculating item costs, working capital from target monthly utilisation, and total project cost).
- Implemented `engine/finance.py` (`build_means_of_finance` registering own_contribution, funding_gap, loan, and subsidy).
- Registered figure IDs match fixture schema: `households`, `our_capacity`, `potential_customers`, `demand`, `competitors`, `competitor_capacity`, `market_gap`, `cost.<item_id>`, `working_capital`, `project_cost`, `own_contribution`, `funding_gap`, `loan`, `subsidy`.
- Tests in `tests/engine/test_market_cost.py` pass cleanly.

