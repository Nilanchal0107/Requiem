# 14: V1 exit check and V2 file map

**What to build:** Proof that V1 is done, and a map showing that every file belongs to exactly one V2 owner. Run both servers, confirm every route renders and every endpoint responds with contract-shaped data, then write the file map V2 developers split the work by.

**V2 owner:** Fullstack (V1 is built by the single developer)

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13

**Status:** done

## Notes

- **Exit criteria** (`docs/prd.md` §10): `npm run dev` and `uvicorn` both run, every route renders, every endpoint responds with contract-shaped data.
- Run the checks from a clean clone (fresh `uv sync`, fresh `npm install`), not from your working copy.
- Write `.scratch/v1-skeleton/v2-file-map.md`: a table of path patterns to V2 owner (Frontend, Fullstack, AIML), plus a short list of **frozen files nobody edits in V2** (`contracts.py`, `contracts.ts`, `pyproject.toml`, `uv.lock`, `package.json`, lockfile, `api/main.py`, the router file, the i18n loader, `fixtures/`).
- For every file under version control, the map must name one owner. If any file needs two owners, fix the skeleton here (split the file) instead of documenting the overlap.
- Where a V2 task still touches a shared file (for example a new i18n namespace or a new engine module), record it as a **known conflict** with the rule that avoids it.
- Anything that fails goes into a new ticket under `.scratch/v1-skeleton/issues/`, not into this one.

## Acceptance criteria

- [x] From a clean clone: `uv sync`, `uv run pytest` (everything passes or is skipped, nothing fails), `uv run uvicorn api.main:app`, and `cd web && npm install && npm run dev` all work.
- [x] All 6 routes render in a browser at 360 px wide without console errors.
- [x] Every one of the 16 endpoints responds with data that validates against its contract model.
- [x] The report flow works: `/new` → Start → stage list → `/reports/:id` with the verdict visible.
- [x] `v2-file-map.md` exists, covers every tracked file, and has no file with two owners.
- [x] The frozen-files list is written and matches what V1 actually left finished.
- [x] Tickets 01–14 are marked done and the work is committed, one ticket per commit.

## Comments

- **Commit:** the `V1-14` commit on `main` (this ticket, `v2-file-map.md`, `check_file_map.py`). Ticket 13 was closed in `2ebcee1`.
- **Clean clone** (`git clone` of `main` at `e13b3ab` into a scratch folder):
  - `uv sync` worked. `uv run pytest`: 86 passed, 5 skipped, 0 failed.
  - `npm install` worked. `npm run build` (`tsc -b` + `vite build`) and `npm run check` pass.
  - `uv run uvicorn api.main:app` and `npm run dev` both serve.
- **Endpoints:** all 16 operations in `/openapi.json` returned 200 through curl with a session cookie: auth register, login, logout and me; localities, archetypes and schemes; intake parse; reports create, list, get and stream; simulate, compare, chat; voice transcribe. FastAPI validates each response against its `response_model`, so a 200 means the response is contract-shaped. The stream sends `event: stage` lines that parse as `StageEvent`. `chat` needs the fixture id `demo-niphad-dairy` (other ids return 404 by design), and `transcribe` takes multipart `audio` and `language`.
- **Routes:** `/`, `/login`, `/new`, `/reports/:id`, `/compare`, `/reports` (and the 404) render with no console errors. In a 360 px iframe each has `innerWidth` 360 and `scrollWidth` ≤ 360. The Chrome window resize did not change the viewport, which is why the iframe was used.
- **Report flow:** on `/new`, Start posts the canned intake, streams the stages, and lands on `/reports/<new uuid>` showing "Feasible" and "Scheme: MUDRA". The stage list itself was not captured mid-stream, since screenshots time out in this harness; ticket 12 verified it.
- **No new tickets.** Two things look odd but match their specs:
  - The Explanation and Compare text shows raw `{{figure_id}}` placeholders. Ticket 13 asked for placeholders left unresolved, and resolving them is V2 Frontend work.
  - `chat` returns empty `figures` while its reply uses `{{funding_gap}}`. The `ChatResponse.reply` comment allows placeholders from the report's figures.
- **File map:** each of the 387 tracked files has exactly one owner, so no file needed splitting. `check_file_map.py` reads the Owners table from `v2-file-map.md`, so the map and the check cannot drift.
- **For V2:** read the Known conflicts section of `v2-file-map.md` before starting. The two most likely to bite are a new endpoint (frozen `api/main.py`) and a new page (frozen `web/src/router.tsx`).
