# 48: Full catalogue and eval (stretch)

**What to build:** The remaining Business Archetypes (onion cultivation, poultry, tailoring, flour mill) and Schemes (KCC, PM Vishwakarma, CMEGP) as sourced data. Then the 15-case eval (5 Archetypes × 3 villages) reports scheme-match accuracy and verifier pass rate.

**Owner:** AIML

**Blocked by:** None (stretch; pick up only when your core tickets are done). Needs 01–03 done.

**Status:** ready-for-agent

## Notes

- Same sourcing rule as 01: `verified_on` only after opening the source, and unconfirmed figures are left out.
- KCC adds bullet repayment and interest subvention to the engine, with a test.

## Acceptance criteria

- [ ] The eval prints accuracy and pass rate. Paste them into this ticket's comment for the pitch.

## Comments

- Commit: `V2-48: Eval harness` (see `git log`). **Partly done: status stays `ready-for-agent`.**
- Done: `llm/eval.py` (`run_eval`, `main`). `uv run python -m llm.eval` builds Archetype × village × persona cases from the catalogue (12 now: new unit expects PMEGP, existing unit expects MUDRA, hand-labelled from the Scheme rules) and prints scheme-match accuracy and verifier pass rate. Test in `tests/llm/test_eval.py`.
- Current output: scheme-match **100%** over 12 cases. Verifier pass rate **0%** only because no recorded replies or API keys exist here; run with `LLM_MODE=live` (or `record`) and paste the real rate.
- **Not done:** the 4 Archetypes (onion, poultry, tailoring, flour mill) and 3 Schemes (KCC, PM Vishwakarma, CMEGP), plus KCC bullet repayment / interest subvention in the engine. CLAUDE.md rule 6 forbids unsourced figures and `verified_on` needs a human to open each `source_url`. Someone has to supply those sourced numbers; the eval picks up new files in `data/` automatically.
