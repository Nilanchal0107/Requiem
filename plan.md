# V2 plan: who builds what, and when

V2 is **1 hour** (0:45–1:45). Three people work at the same time, each in their own folder of code and their own folder of tickets. Nobody waits on anyone else. V3 (merge) gets its own hour after this.

- Spec: `.scratch/v2-parallel/spec.md` (read the "Grilling decisions" section first)
- Words to use: `CONTEXT.md` (Entrepreneur, Own Contribution, Figure id, …)
- Which files you may edit: `.scratch/v1-skeleton/v2-file-map.md`

## Your tickets

| Persona | Ticket folder | You may edit | Core tickets (in order) |
|---|---|---|---|
| **AIML** | `.scratch/v2-parallel/aiml/` | `engine/`, `llm/`, `data/`, their tests | 01 → 04 → 02 → 03 → 05 → 06 |
| **Fullstack** | `.scratch/v2-parallel/fullstack/` | `api/`, API tests, root config | 10 → 11 → 12 → 13 |
| **Frontend** | `.scratch/v2-parallel/frontend/` | `web/` (not `contracts.ts`) | 20 → 21 → 22 → 23 → 24 |

Tickets numbered **40+** in your folder are **stretch**. Touch them only once your core tickets are done.

## Timetable

| Time | AIML | Fullstack | Frontend |
|---|---|---|---|
| 0:45 | 01 Demo catalogue and villages | 10 Real auth | 20 Numbers and "Why this number?" |
| ~1:00 | 04 Verifier | 11 Report persistence | 21 Wizard posts real intake |
| ~1:10 | 02 Engine: market, cost, Funding Gap | 12 Stream stores and replays | 22 Report tabs and Bank View |
| ~1:20 | 03 Engine: Scheme, loan, Verdict | 13 Pipeline driver | 23 What-if sheet |
| ~1:35 | 05 LLM client and Entrepreneur View | stretch or V3 prep | 24 Language switch and account menu |
| ~1:45 | 06 Path to Yes (drop first if late) | | |

If you fall behind, drop from the bottom of your column. **Protected:** Bank View (22), Entrepreneur View with verifier (04, 05, 20), what-if (23) and Verdict (03).

## How to work one ticket

1. **Pick:** the lowest-numbered ticket in your folder with `Status: ready-for-agent` whose `Blocked by:` tickets are all `done`.
2. **Start:** run `/clear` so the context is fresh, then give Claude the ticket path, for example:
   `Implement .scratch/v2-parallel/aiml/01-demo-catalogue-and-niphad-villages.md`
3. **Build:** edit only the folders your persona may edit. If you need something outside them, write it in the ticket's comment instead and tell the owner.
4. **Check:**
   - AIML and Fullstack: `uv run pytest` is green.
   - Frontend: `cd web && npm run check && npm run build` pass, and the screen works at 360 px.
5. **Close the ticket file:**
   - set `Status: done`
   - tick the checkboxes that now hold
   - add a `## Comments` section with the commit hash, anything deferred, and notes for later tickets
6. **Commit:** one commit per ticket, with the code and the ticket file together, message `V2-NN: <title>`.

## Rules that bite in V2

- **Don't edit frozen files:**
  - `api/contracts.py` and `web/src/types/contracts.ts`
  - `pyproject.toml`, `uv.lock`, `web/package.json` and the web lockfile
  - `api/main.py`
  - `web/src/router.tsx`
  - the i18n loader
  - `fixtures/`
- **The API keeps serving fixtures** (`USE_FIXTURES=1`). Frontend builds against fixture data. Real engine and LLM output reaches the screens in V3.
- **No digits in LLM text.** Numbers are `{{figure_id}}` placeholders only. Keep the fixture's Figure ids, and add new ones rather than renaming.
- **Scheme figures need a source.** Set `verified_on` only after you've opened the `source_url`. Never invent a figure.

## Done = V2 exit

- [ ] Every core ticket in all three folders is `done` (or explicitly dropped, with a note).
- [ ] `uv run pytest` is green.
- [ ] `npm run check` and `npm run build` pass.
- [ ] `uv run python .scratch/v1-skeleton/check_file_map.py` passes.
