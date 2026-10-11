# Code computes every number and the Verdict; the LLM only explains

Most GenAI advisors let the model estimate costs, pick schemes and judge feasibility, which produces confident numbers that change between runs and cannot be defended to a bank or a judge. We decided that every figure in a DPR (Project Cost, Funding Gap, subsidy, EMI, projections, DSCR, break-even), every Scheme eligibility decision and the Verdict itself come from deterministic code over curated JSON and stored Locality data. The LLM only turns free text into form fields, writes the Entrepreneur View and answers chat questions, and a verifier rejects any LLM text whose numbers don't match the engine.

## Consequences

- The what-if simulator and Comparison never call the LLM, so they are instant and work without network access.
- Business Archetypes and Schemes outside the curated JSON cannot be evaluated properly; they get an "Assumption" Source Badge instead of being invented.
- Adding a Scheme or Archetype means editing JSON and its rules, not changing a prompt.
