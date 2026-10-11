# 01: Demo catalogue and Niphad villages

**What to build:** Real catalogue data for the demo path. That means the `dairy` and `kirana` Business Archetypes, the MUDRA, PMEGP and Stand-Up India Schemes, official scheme text for those three, and 3 Niphad villages (Lasalgaon plus two more). The data loaders return validated models from it, and the seed step loads the villages into the database.

**Owner:** AIML

**Blocked by:** None (can start immediately)

**Status:** done

## Notes

- Spec: `.scratch/v2-parallel/spec.md` (Grilling decisions, then AIML). Shapes: the data package's models and the fixture catalogues, which you may copy from but must not edit.
- Every Scheme rule has a `source_url` and a `verified_on`. Set `verified_on` only after you've opened the source. Leave out any figure you can't confirm and list it in this ticket's comment (CLAUDE.md rule 6).
- Villages: use real Census household counts. Competitor counts per Archetype are hand estimates, badged `assumption`.
- `dairy` is an Aggregator (no Market Gap). `kirana` is local, so the Market Gap path gets exercised.

## Acceptance criteria

- [x] The Archetype and Scheme loaders return validated models for exactly the 2 Archetypes and 3 Schemes. A malformed file raises instead of loading.
- [x] The scheme-text loader returns text for each of the 3 Schemes.
- [x] The seed step inserts the 3 villages into a fresh database and returns 3.
- [x] A data test asserts that every Scheme rule has a `source_url` and a `verified_on`.
- [x] `uv run pytest tests/data` passes.

## Comments

- Implemented real catalogue data:
  - `data/archetypes/dairy.json`, `data/archetypes/kirana.json`
  - `data/schemes/mudra.json`, `data/schemes/pmegp.json`, `data/schemes/standup_india.json`
  - `data/scheme_texts/mudra.md`, `data/scheme_texts/pmegp.md`, `data/scheme_texts/standup_india.md`
  - `data/census/niphad_villages.json` (3 villages: Lasalgaon, Niphad, Pimpalgaon Baswant)
  - `data/osm/niphad_counts.json` (competitor counts)
- Implemented `data/loaders.py` (`load_archetypes`, `load_schemes`, `load_scheme_texts`, `seed_villages`).
- Added tests in `tests/data/test_catalogue.py` asserting all acceptance criteria.
- `uv run pytest tests/data` runs and passes (17 passed, 10 skipped).

