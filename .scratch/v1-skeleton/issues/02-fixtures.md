# 02: Fixtures

**What to build:** The sample data every V1 endpoint and page runs on, so the frontend can build every screen before the engine exists. After this ticket there is one complete `Report` for the demo persona (dairy, 5 animals, a Niphad village, ₹1,00,000 Own Contribution, female, OBC, 10th pass, language `mr`), the canned stage events, and fixture catalogues.

**V2 owner:** Fullstack (V1 is built by the single developer)

**Blocked by:** 01

**Status:** done

## Notes

- The report's `EngineResult.figures` must contain **every** Figure in the result, keyed by id, using the ids in `docs/trd.md` §5.9. Numbers must be internally consistent (Project Cost, Funding Gap, EMI, repayment rows closing at exactly 0). Hand-check the EMI against a bank calculator. These are fixture numbers only, not engine output.
- The explanation text is Marathi and contains only `{{figure_id}}` placeholders, never digits. `verified` and `total` match the placeholder count.
- Fixture localities: Nashik district, Niphad block, at least 3 villages including Lasalgaon, with household counts.
- Fixture archetypes: all 6, with unit-scale bounds and eligibility fields. Fixture schemes: all 6.
- **Rule 6 applies in spirit:** fixture scheme figures are illustrative. Use official URLs only where `docs/` gives them, use an obviously fake placeholder URL otherwise, and set `verified_on` to `1970-01-01` so nobody mistakes fixture data for verified data. Add a short `fixtures/README.md` saying the data is illustrative and replaced from `data/` in V3.
- The fixture files are frozen after V1.

## Acceptance criteria

- [x] The fixture folder holds a report, canned stage events (all 6 stages, running then done, with durations and sources), and localities, archetypes and schemes catalogues.
- [x] A test loads each fixture through the matching contract model and passes.
- [x] The report's placeholders all resolve against `engine.figures`, and a test asserts it.
- [x] No raw digit appears in the explanation text outside a placeholder (a test asserts it).
- [x] The verdict, scheme and loan figures tell a coherent story (e.g. MUDRA or PMEGP tier chosen, DSCR consistent with the projections).
- [x] The fixtures README states they are illustrative.

## Comments

- Done in `d7a08e8` (fixtures and `tests/test_fixtures.py`, 15 tests passing).
- **Not met:** the notes ask for the EMI to be hand-checked against a bank calculator. The test checks the closed-form formula only (EMI ₹9,632, exact 9,631.81), not an external calculator, and it assumes the fixture's own `n = tenure − moratorium` convention. Needs a manual check before the freeze.
- **Growth set to 0** in the fixture. TRD §5.3 applies growth after the sales ceiling, so 5% growth pushed year-4 units past the 1,200 L capacity. Decide the TRD ordering fix with AIML; the fixture follows the TRD formula with growth 0.
- **Contract vs TRD (AIML to decide):** `MarketAnalysis.market_gap` (and `potential_customers`, `demand`, `competitors`, `competitor_capacity`) are required Figures, but TRD §5.2 says aggregator mode produces no market gap. Fixture uses zero values with notes. The aggregator `market_gap` signal is omitted (TRD §5.7: local mode only).
- **Contract gaps:** `YearProjection` and `RepaymentRow` are bare ints with no Source Badge (CLAUDE.md rule 7); `our_capacity` is labelled litres but the `Unit` enum has no litres (uses `count`).
- **Ineligible list empty:** `SchemeMatch.ineligible` is empty, since the fixture schemes carry no sector field to filter on.
- **Copy:** the Marathi text is written but not checked by a native speaker.
- Test ownership: `tests/test_fixtures.py` sits outside the listed persona folders; Fullstack to confirm.
