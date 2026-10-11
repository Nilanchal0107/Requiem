# V2 file map

Every tracked file has exactly one V2 owner. Split the V2 work by this table. Check it with `uv run python .scratch/v1-skeleton/check_file_map.py`, which fails if a tracked file has no owner or more than one. When V2 adds a file, it falls under an existing row, so the map only changes if a new top-level folder appears.

`*` matches across folders. `Except` removes paths from a row.

## Owners

| Pattern | Owner | Except |
|---|---|---|
| `web/*` | Frontend | `web/src/types/contracts.ts` |
| `web/src/types/contracts.ts` | Fullstack | |
| `api/*` | Fullstack | |
| `fixtures/*` | Fullstack | |
| `tests/__init__.py` | Fullstack | |
| `tests/test_api_smoke.py` | Fullstack | |
| `tests/test_fixtures.py` | Fullstack | |
| `pyproject.toml` | Fullstack | |
| `uv.lock` | Fullstack | |
| `.python-version` | Fullstack | |
| `.gitignore` | Fullstack | |
| `.env.example` | Fullstack | |
| `CLAUDE.md` | Fullstack | |
| `CONTEXT.md` | Fullstack | |
| `plan.md` | Fullstack | |
| `docs/*` | Fullstack | |
| `.scratch/*` | Fullstack | |
| `.claude/*` | Fullstack | |
| `engine/*` | AIML | |
| `llm/*` | AIML | |
| `data/*` | AIML | |
| `tests/engine/*` | AIML | |
| `tests/llm/*` | AIML | |
| `tests/data/*` | AIML | |
| `tests/test_verifier.py` | AIML | |

At V1 exit (`e13b3ab`) this assigns 387 tracked files: Frontend 121, Fullstack 229, AIML 37.

Notes on the less obvious rows:

- `docs/`, `CLAUDE.md`, `CONTEXT.md` and `.scratch/` go to Fullstack because CLAUDE.md gives root config to Fullstack and no persona owns docs. Anyone can still add a comment to their own ticket file.
- `.claude/` holds vendored agent skills, not app code. No V2 work is planned there.
- `tests/data/` goes to AIML because `data/` is AIML's.

## Frozen files (nobody edits in V2)

| File | Why |
|---|---|
| `api/contracts.py` | Frozen API contract (CLAUDE.md rule 3). |
| `web/src/types/contracts.ts` | Generated from `contracts.py`, never hand-edited. |
| `pyproject.toml`, `uv.lock` | Python dependencies are settled. |
| `web/package.json`, `web/package-lock.json` | Web dependencies are settled. |
| `api/main.py` | All eight routers are already registered. |
| `web/src/router.tsx` | All six routes plus 404 are already declared. |
| `web/src/i18n/index.ts`, `web/src/i18n/resolve.ts` | The i18n loader globs `./*/*.json`, so a new namespace is only a new file. |
| `fixtures/*` | The V1 contract examples. `tests/test_fixtures.py` validates them against the models. |

## Known conflicts

These are V2 tasks that would touch a shared or frozen file, with the rule that avoids the clash.

1. **A new endpoint** would need an `include_router` line in frozen `api/main.py`. Rule: add the route to one of the eight existing modules (`auth`, `catalog`, `intake`, `reports`, `simulate`, `compare`, `chat`, `voice`).
2. **A new page** would need frozen `web/src/router.tsx`. Rule: build it inside an existing route (a tab, sheet or step file under `web/src/pages/<route>/`).
3. **A contract change** touches `api/contracts.py` and `web/src/types/contracts.ts`. Rule: only Fullstack makes it, with all three personas agreeing, and commits both files together after regenerating `contracts.ts` (CLAUDE.md rule 3).
4. **A new i18n namespace** needs no loader edit. Rule: Frontend adds `web/src/i18n/{en,hi,mr}/<namespace>.json`. Missing `hi` and `mr` keys fall back to `en`.
5. **A new engine or LLM module** stays in `engine/` or `llm/` (AIML), but it is called from `api/pipeline.py` (Fullstack). Rule: AIML exposes a function whose arguments and return types are contract models, and Fullstack makes the one-line call in `pipeline.py`.
6. **New Scheme or Archetype data** goes in `data/schemes/` and `data/archetypes/` (AIML). Rule: the API reads it only through `data/loaders.py`. Fullstack does not edit loaders. It asks AIML.
7. **Tests needing different data** must not edit `fixtures/`. Rule: build the input inside the test file, or derive it from a fixture in code.
