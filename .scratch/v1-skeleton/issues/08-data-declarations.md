# 08: Data declarations

**What to build:** The `data/` package, its folder layout and the models that describe the hand-curated JSON, with no catalogue content yet. After this ticket V2 adds one JSON file per Archetype or Scheme, so two people never edit the same file.

**V2 owner:** AIML (V1 is built by the single developer)

**Blocked by:** 01

**Status:** done

## Notes

- **Layout (decided):** `data/archetypes/<id>.json` and `data/schemes/<id>.json`, one file per item. This deliberately replaces the single `archetypes.json` and `schemes.json` in `docs/trd.md` §4.1–4.2. The shape of each item stays as in the TRD. Update nothing outside `data/` in this ticket; note the TRD change for the doc owner.
- Declare the data models that describe an item: archetype (unit scale, cost items, revenue, operating cost, market mode, competitor tags, channels, notes) and scheme (rules, tiers, subsidy, loan terms, `source_url`, `verified_on`). Making `source_url` and `verified_on` required on every scheme is how rule 6 gets enforced.
- Declare the loader functions (all archetypes, all schemes, scheme texts for retrieval) and the idempotent village seed function. All raise `NotImplementedError`.
- Create the folders `archetypes/`, `schemes/`, `scheme_texts/`, `census/`, `osm/` and `llm_cache/`, each holding only a placeholder so git keeps them.
- **No scheme or archetype figures are created in this ticket.** Rule 6: never invent scheme figures. The first real data is a V2 ticket.
- The engine does not import `data`. The API will pass loader output into the engine as plain dicts or models.

## Acceptance criteria

- [x] The package imports cleanly; it imports `api.contracts` at most, and never the engine or the LLM layer.
- [x] The scheme model rejects an item without `source_url` or `verified_on` (a test builds one without each and expects a validation error).
- [x] All the folders above exist and are tracked.
- [x] The loader and seed signatures are declared with docstrings naming the folder they read and the table they write.
- [x] No JSON catalogue content exists yet.

## Comments

- Implemented in `data/models.py`, `data/loaders.py`, `tests/data/test_declarations.py` and the six `.gitkeep` placeholders. Full suite: 86 passed, 5 skipped. `mypy data tests/data` clean (ad hoc `uv run --with mypy`; mypy is not a project dependency).
- **TRD change for the doc owner:** the catalogue is one file per item (`data/archetypes/<id>.json`, `data/schemes/<id>.json`), replacing `data/archetypes.json` and `data/schemes.json` in TRD §4.1–4.2. Item shape is unchanged.
- Code review (`/code-review`, medium) fixes applied: all models reject unknown keys (`extra="forbid"`, so a typo like `whn` fails loudly), `Archetype.notes` added, `Scheme.source_url` must be an http(s) URL.
- **Deferred to V2 (first real data):** cross-field checks (subsidy type vs rates, aggregator Market needs `aggregator`, moratorium within tenure), numeric bounds on percentages and months, and `UnitScale` invariants (step > 0, default within min/max). Add when the first catalogue JSON lands.
- Placeholders are committed so the folders exist in a fresh clone.

