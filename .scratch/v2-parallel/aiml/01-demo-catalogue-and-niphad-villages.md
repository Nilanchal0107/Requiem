# 01: Demo catalogue and Niphad villages

**What to build:** Real catalogue data for the demo path. That means the `dairy` and `kirana` Business Archetypes, the MUDRA, PMEGP and Stand-Up India Schemes, official scheme text for those three, and 3 Niphad villages (Lasalgaon plus two more). The data loaders return validated models from it, and the seed step loads the villages into the database.

**Owner:** AIML

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## Notes

- Spec: `.scratch/v2-parallel/spec.md` (Grilling decisions, then AIML). Shapes: the data package's models and the fixture catalogues, which you may copy from but must not edit.
- Every Scheme rule has a `source_url` and a `verified_on`. Set `verified_on` only after you've opened the source. Leave out any figure you can't confirm and list it in this ticket's comment (CLAUDE.md rule 6).
- Villages: use real Census household counts. Competitor counts per Archetype are hand estimates, badged `assumption`.
- `dairy` is an Aggregator (no Market Gap). `kirana` is local, so the Market Gap path gets exercised.

## Acceptance criteria

- [ ] The Archetype and Scheme loaders return validated models for exactly the 2 Archetypes and 3 Schemes. A malformed file raises instead of loading.
- [ ] The scheme-text loader returns text for each of the 3 Schemes.
- [ ] The seed step inserts the 3 villages into a fresh database and returns 3.
- [ ] A data test asserts that every Scheme rule has a `source_url` and a `verified_on`.
- [ ] `uv run pytest tests/data` passes.
