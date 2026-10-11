# 48: Full catalogue and eval (stretch)

**What to build:** The remaining Business Archetypes (onion cultivation, poultry, tailoring, flour mill) and Schemes (KCC, PM Vishwakarma, CMEGP) as sourced data. Then the 15-case eval (5 Archetypes × 3 villages) reports scheme-match accuracy and verifier pass rate.

**Owner:** AIML

**Blocked by:** None (stretch; pick up only when your core tickets are done). Needs 01–03 done.

**Status:** done

## Notes

- Same sourcing rule as 01: `verified_on` only after opening the source, and unconfirmed figures are left out.
- KCC adds bullet repayment and interest subvention to the engine, with a test.

## Acceptance criteria

- [x] The eval prints accuracy and pass rate. Paste them into this ticket's comment for the pitch. *(scheme-match pasted below; the verifier pass rate needs an LLM key, see Comments)*

## Comments

- Commits: `V2-48: Eval harness` (harness), then `V2-48: Full catalogue and eval` (this change). See `git log`.
- **Eval numbers (`uv run python -m llm.eval`):** 36 cases (6 Archetypes × 3 villages × new/existing Entrepreneur). Scheme-match **100%**. Verifier pass rate **0% here only because there is no `GEMINI_API_KEY`/`GROQ_API_KEY` and no recorded replies**; run `LLM_MODE=live uv run python -m llm.eval` once with a key and paste the real rate for the pitch. The ticket said 15 cases (5 × 3); the catalogue has 6 Archetypes and each is run as both a new and an existing unit, so it is 36.
- **Archetypes added** (`data/archetypes/`): `onion_cultivation` (agri, aggregator: Lasalgaon APMC), `poultry`, `tailoring`, `flour_mill` (all local). Cost, price and yield figures are hand estimates badged as 2026 assumptions in each `note`, like dairy and kirana. Competitor counts for the three local ones in `data/osm/niphad_counts.json` are hand estimates too, not an OSM pull.
- **Schemes added** (`data/schemes/`, text in `data/scheme_texts/`), each opened on 2026-10-11:
  - `kcc` — source: PIB release 2131989 (28 May 2025). 7% rate, ₹3 lakh limit, 3% prompt-repayment incentive (so 4%), ₹2 lakh for animal husbandry/fisheries. Left out: the ₹5 lakh limit from Budget 2025 (a March 2026 PIB backgrounder reportedly says so, but PIB returned 403 to the fetcher and the Cabinet release I read says ₹3 lakh), and the repayment period (the release says only "short-term"; **12 months and bullet repayment are my modelling assumption**, so KCC is a 12-month loan renewed each cycle).
  - `pm_vishwakarma` — source: pmvishwakarma.gov.in. ₹1 lakh first tranche, 18 months, 5%. Left out: the ₹2 lakh second tranche (30 months; the page says nothing on when it unlocks), the ₹15,000 toolkit grant (flat amount, no field for it), one-per-family.
  - `cmegp` — source: the Bank of Maharashtra CMEGP page, **not** the state portal. Reason: `maitri.maharashtra.gov.in` fails TLS verification here and I did not bypass it. Used: age 18–45 (50 for women and SC/ST), new units only, 5%/10% contribution, 15/25/25/35% back-ended subsidy, 36-month lock-in, ₹50 lakh manufacturing cap, negative list (dairy and poultry are excluded). Left out: the service/agro project cost cap (that page says ₹10 lakh, MAITRI via search says ₹20 lakh; **someone with a working browser should check the state portal and add it**), the education rule, and a CMEGP interest rate (none is fixed, so 10% is an `assumption` as for PMEGP).
- **Engine** (`engine/`): `bullet` repayment (one payment of P×(1+r)^tenure at the last month; `LoanTerms.emi` carries that single payment, since the frozen contract has no other field); `interest_subvention` (the Entrepreneur's rate is the Scheme rate minus the subvention, and it is not counted again in ranking); rule ops `ne` and `not_in` (they existed in the data model but silently failed); `funding_gap` is now addressable in rules, with an "₹X more Own Contribution" hint; `build_means_of_finance` now reads the Scheme's own subsidy block instead of checking for `"pmegp"` (needed so CMEGP's subsidy shows); rank ties go to the lower rate paid. A bullet loan is judged on payback against the 60-month horizon instead of its 12-month tenure, since KCC is renewed each cycle; without this no crop could ever be feasible.
- Tests: `tests/engine/test_full_catalogue.py`, updated `tests/data/test_catalogue.py` and `tests/llm/test_eval.py`. Full suite green.
- **For other tickets / owners:**
  - Fullstack/Frontend: for a KCC loan `terms.emi` is the single end-of-tenure payment, not monthly. Label it "one payment" in the UI when `tenure_months` ≤ 12 and the schedule has zeros before the last month. The catalogue endpoint now returns 6 Archetypes.
  - Pre-existing, not changed: with no loan (Own Contribution covers the Project Cost) `min_dscr` is 0.0 and the Verdict comes out `not_feasible`. Path to Yes reads `best_scheme.get("max_tenure_months")` from the top level of the Scheme, but the field is under `loan`, so tenure suggestions never fire.
