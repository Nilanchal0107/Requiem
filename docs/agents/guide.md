# V2 Team Guide: Branches, Agents, Merges

Three people, three personas, AI agents write the code. This page is the whole workflow.

## Who owns what

| Persona | Owns |
|---|---|
| Frontend | `web/` (except `web/src/types/contracts.ts`) |
| Fullstack | `api/`, `web/src/types/contracts.ts`, `fixtures/`, `tests/test_api_smoke.py`, root config |
| AIML | `engine/`, `llm/`, `data/`, `tests/engine/`, `tests/test_verifier.py` |

Full per-file map: `.scratch/v1-skeleton/v2-file-map.md`. If a file isn't yours, don't edit it. Write the change you need into your ticket instead.

**Frozen in V2 (nobody edits):** `api/contracts.py`, `web/src/types/contracts.ts`, `pyproject.toml`, `uv.lock`, `package.json`, `package-lock.json`, `api/main.py`, the router file, the i18n loader, `fixtures/`.

## Branches

- **One branch per ticket**, from fresh `main`:
  ```
  git switch main && git pull
  git switch -c v2/<persona>/<ticket-no>-<short-name>
  # e.g. v2/aiml/03-scheme-matcher
  ```
- **Small, short-lived branches.** Merge a ticket as soon as it's done. Don't wait until the end.
- **Pull `main` into your branch at least once an hour:** `git pull origin main`.
- **Nobody commits straight to `main`.** The Fullstack owner does all merges.

## Running AI agents

- **One agent per checkout.** To run two agents on one laptop, give each its own folder:
  ```
  git worktree add ../requiem-<ticket> -b v2/<persona>/<ticket>
  ```
- **Start every agent prompt with:** the ticket file path, your persona, and "edit only these folders: …".
- **Check what the agent touched before you push:**
  ```
  git diff --stat main...
  ```
  Undo any file outside your folders.
- Agents follow `CLAUDE.md`. The rules that matter most: the engine computes every number, LLM text contains no digits, every number carries a Source Badge.

## Before asking for a merge

Run these on your branch, and paste the results in the ticket's `## Comments` section:

```
uv run pytest                  # nothing fails
cd web && npm run build        # builds clean
```

Then click through `/new` → Start → `/reports/:id` and confirm the Verdict shows.

Finally, update the ticket file (`Status: done`, tick the criteria, add the commit hash) and tell the Fullstack owner it's ready.

## Merging (Fullstack owner)

1. `git switch main && git pull`
2. `git merge --no-ff v2/<persona>/<ticket>`
3. Re-run `uv run pytest` and `npm run build` on `main`.
4. Push, then tell the team: "main updated, pull it."

## Contract and dependency changes

- **API contract:** only Fullstack changes it, directly on `main`. Change `api/contracts.py`, regenerate `contracts.ts`, and commit both together:
  ```
  npx openapi-typescript http://localhost:8000/openapi.json -o web/src/types/contracts.ts
  ```
  Everyone else then pulls `main`.
- **New package (`uv add` / `npm install x`):** ask Fullstack. Lockfile edits on two branches always conflict.

## Shared-file conflicts

- **i18n strings:** add a new namespace file. Don't edit someone else's.
- **New engine module:** add a new file. Keep edits to `engine/__init__.py` to a single line.
- **If a merge conflicts anyway,** the branch owner resolves it on their own branch after pulling `main`. Never resolve it on `main`.

## Working without waiting on others

- **Frontend:** build against `fixtures/` and the mocked endpoints. Don't wait on AIML or Fullstack.
- **AIML:** test `engine/` with plain `assert`s. It has no network, DB, or LLM, so it never needs the API running.
- **Fullstack:** keep the endpoints returning fixture-shaped data until the real engine merges.

## Stuck?

If you're blocked more than 15 minutes, say so in the team chat with the ticket number. Don't let your agent start "fixing" someone else's folder.
