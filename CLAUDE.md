# Requiem: Hyper Local Business & Loan Advisory

A GenAI web app that builds a bank-format DPR for a rural Entrepreneur from their Locality, Business Archetype and Own Contribution, then explains it in English, Hindi or Marathi. Hackathon build: 3 people, 5 hours, localhost demo for Niphad, Nashik.

- **Spec:** `docs/prd.md` is the source of truth for scope, API contract, routes and delivery plan.
- **Vocabulary:** `CONTEXT.md`. Use its terms in code, UI copy and commits (Entrepreneur, not "user"; Own Contribution, not "capital").
- **Decisions:** `docs/adr/`.

## Non-negotiable rules

1. **Code computes, the LLM explains** (ADR 0001). Every number, Scheme match and Verdict comes from `engine/`. Never let an LLM produce or change a number.
2. **`engine/` is pure Python.** No network, DB, LLM or file I/O inside it. Every function has at least one `assert` check.
3. **The API contract is frozen after V1.** `api/contracts.py` is the only source; `web/src/types/contracts.ts` is generated (`npx openapi-typescript http://localhost:8000/openapi.json -o web/src/types/contracts.ts`) and never hand-edited. Changes need all three to agree; the Fullstack owner commits both files together.
4. **LLM text never contains digits.** Numbers appear only as `{{figure_id}}` placeholders that the frontend fills from `EngineResult.figures`; the verifier rejects anything else.
5. **Stay in your folder:**

   | Persona | Owns |
   |---|---|
   | Frontend | `web/` (except `web/src/types/contracts.ts`) |
   | Fullstack | `api/`, `web/src/types/contracts.ts`, `fixtures/`, `tests/test_api_smoke.py`, root config (`pyproject.toml`, `.env.example`) |
   | AIML | `engine/`, `llm/`, `data/`, `tests/engine/`, `tests/test_verifier.py` |

   When working a ticket, edit only the owning persona's folders. If you need a change elsewhere, note it in the ticket instead.
6. **Scheme and Archetype data is hand-curated JSON** in `data/`, with `source_url` and `verified_on` on every Scheme rule. Never invent scheme figures.
7. **Every number shown carries a Source Badge** (`census`, `osm`, `user`, `assumption`, `scheme`, `computed`).
8. Secrets only in `.env` (git-ignored). Commit `.env.example`.

## Stack

uv + Python 3.12 · FastAPI + SQLModel + SQLite (`DATABASE_URL` can point to Neon) · React + Vite + TypeScript + React Router + Tailwind + shadcn/ui + Recharts · own `t()` i18n · `openai` SDK against Gemini (primary) and Groq (fallback), `LLM_MODE=live|record|replay` · BM25 only. Details in `docs/trd.md`; components and flows in `docs/architecture.md`; endpoints in `docs/api-contracts.md`.

## UI

Most Entrepreneurs are rural and on budget Android phones: **design mobile-first at 360 px**. Follow `docs/ui-ux.md` (tokens, components, copy rules) and `docs/wireframes.md` (screens). Light theme, Mukta font, Lucide icons, 48 px touch targets, one amber primary button per screen, icon + word on every option, plain language outside the Bank DPR tab.

## Agent skills

### Issue tracker

Issues and specs are local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`. Tickets are grouped by version (`.scratch/v1-skeleton/`, `.scratch/v2-parallel/`, `.scratch/v3-merge/`), and each ticket names its owner persona and `Blocked by:` tickets.

**After executing a ticket, update its file:** set `Status: done`, tick the acceptance-criteria checkboxes that now hold, and append a `## Comments` section with the commit hash, anything deferred, and notes for tickets that build on it. Commit the ticket update with the work.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
