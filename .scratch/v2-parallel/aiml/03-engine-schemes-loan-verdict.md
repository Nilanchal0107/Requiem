# 03: Engine: Scheme match, loan, projections and Verdict

**What to build:** `run_engine` returns a complete `EngineResult` for the demo persona and for kirana in all 3 villages. That covers the Scheme match with reasons and unlock hints, loan terms, the repayment schedule, 5-year projections, DSCR, break-even, payback and the Verdict. Path to Yes is still off (ticket 06).

**Owner:** AIML

**Blocked by:** 02

**Status:** ready-for-agent

## Notes

- Scheme eligibility is evaluated from the rule data, with one evaluator for all three Schemes. The only code specific to a Scheme is its repayment shape: MUDRA tiers, and PMEGP's back-ended subsidy, which reduces outstanding principal at the end of lock-in and not before.
- The Verdict is the worst of four signals: minimum DSCR, Market Gap (local Archetypes only), payback against tenure, and whether any Scheme is eligible.
- Integer rupees. Rates are percent and durations are months.

## Acceptance criteria

- [ ] The EMI matches a hand-checked bank-calculator value.
- [ ] The repayment schedule closes at exactly zero.
- [ ] The PMEGP subsidy changes the outstanding balance exactly at the end of lock-in, and not before.
- [ ] MUDRA tier selection is correct on each side of a tier boundary.
- [ ] An Own Contribution below a Scheme's minimum produces an unlock hint.
- [ ] The Verdict takes the worst signal (one test where only one signal is bad).
- [ ] `run_engine` with Path to Yes disabled returns a contract-valid `EngineResult` for every Archetype × village pair (6 cases).
