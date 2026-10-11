# 03: Engine: Scheme match, loan, projections and Verdict

**What to build:** `run_engine` returns a complete `EngineResult` for the demo persona and for kirana in all 3 villages. That covers the Scheme match with reasons and unlock hints, loan terms, the repayment schedule, 5-year projections, DSCR, break-even, payback and the Verdict. Path to Yes is still off (ticket 06).

**Owner:** AIML

**Blocked by:** 02

**Status:** done

## Notes

- Scheme eligibility is evaluated from the rule data, with one evaluator for all three Schemes. The only code specific to a Scheme is its repayment shape: MUDRA tiers, and PMEGP's back-ended subsidy, which reduces outstanding principal at the end of lock-in and not before.
- The Verdict is the worst of four signals: minimum DSCR, Market Gap (local Archetypes only), payback against tenure, and whether any Scheme is eligible.
- Integer rupees. Rates are percent and durations are months.

## Acceptance criteria

- [x] The EMI matches a hand-checked bank-calculator value.
- [x] The repayment schedule closes at exactly zero.
- [x] The PMEGP subsidy changes the outstanding balance exactly at the end of lock-in, and not before.
- [x] MUDRA tier selection is correct on each side of a tier boundary.
- [x] An Own Contribution below a Scheme's minimum produces an unlock hint.
- [x] The Verdict takes the worst signal (one test where only one signal is bad).
- [x] `run_engine` with Path to Yes disabled returns a contract-valid `EngineResult` for every Archetype × village pair (6 cases).

## Comments

- Implemented `engine/schemes.py` (`match_schemes` evaluating rule predicates, Own Contribution requirements, subsidy rates, MUDRA tier selection, ranking by effective rate, and generating unlock hints).
- Implemented `engine/finance.py` (`build_loan_terms`, `repayment_schedule` closing at zero and handling back-ended subsidy at lock-in, `monthly_operating`, `project_years`, `break_even_month`, `payback_months`, `min_dscr`).
- Implemented `engine/verdict.py` (`decide_verdict` computing worst of dscr, market_gap, payback, and scheme signals).
- Updated `data/archetypes/kirana.json` customer throughput factor to 0.003 so unit_scale throughput fits retail economics.
- Implemented tests in `tests/engine/test_finance_verdict.py` verifying all acceptance criteria. All 21 tests in `tests/engine` pass.

