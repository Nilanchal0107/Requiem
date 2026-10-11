# 13: Pipeline driver

**What to build:** `run_pipeline` is written and ready for V3. It runs the intake, market, cost, schemes, DPR and explanation stages as stage events, stores the engine result and explanation, and still completes the report, with the explanation marked unavailable, when the LLM fails.

**Owner:** Fullstack

**Blocked by:** 12

**Status:** ready-for-agent

## Notes

- It calls `run_engine` and `explain_report` once each, through their declared signatures (known conflict 5). Catalogues and the village come through the data loaders only.
- It isn't reachable while `USE_FIXTURES=1`, so V3 exercises it. Here it only has to import and type-check.

## Acceptance criteria

- [ ] `run_pipeline` imports cleanly, with no remaining `NotImplementedError`.
- [ ] The stage order matches the contract's stage list.
- [ ] Read through the LLM-failure path: it yields an explanation-unavailable stage and still ends with done. Leave a note in the comment for V3 to test it.
