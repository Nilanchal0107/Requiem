# Requiem: Hyper Local Business & Loan Advisory

A GenAI web app that helps a first-time rural **Entrepreneur** answer three questions before they walk into a bank:

1. Will this business work in **my** Locality?
2. How much money do I need, and how much must I borrow?
3. Which government Scheme can I get, and what will I repay?

The Entrepreneur picks their **Locality** (village), a **Business Archetype** (dairy, tailoring, kirana, poultry, flour mill, onion cultivation) and their **Own Contribution**. The app builds a bank-format **DPR** (Detailed Project Report) with deterministic code, then explains it in **English, Hindi or Marathi**.

> Other apps give advice. Ours builds the document you take to the bank, and explains every number in your language.

Built for the Requiem Hackathon 2026 (3 people, 5 hours). The demo Locality is **Niphad block, Nashik district, Maharashtra**.

---

## Core idea: code computes, the LLM explains

Every number, Scheme match and Verdict comes from the pure-Python `engine/`. The LLM only writes the explanation, and it is **never allowed to write a digit**. Numbers appear in LLM text as `{{figure_id}}` placeholders (for example `{{cost.animals}}`), which a verifier checks and the frontend fills from the engine's figures. Every number on screen carries a **Source Badge** (`census`, `osm`, `user`, `assumption`, `scheme`, `computed`).

See [ADR 0001](docs/adr/0001-code-computes-llm-explains.md).

## Features

- **Guided intake wizard** (where, business, money, about you), plus a free-text "describe your idea" box parsed by the LLM.
- **Hyper-local market analysis** from Census village data and OpenStreetMap competitor counts (static file or live Overpass).
- **Scheme matching and loan calculator** for MUDRA, PMEGP, CMEGP, KCC, PM Vishwakarma and Stand-Up India, from hand-curated rules with `source_url` and `verified_on`.
- **Verdict**: Feasible, Feasible with changes, or Not feasible, plus **Path to Yes** (the smallest changes that make it feasible).
- **Bank View**: cost breakdown, means of finance, projections and repayment schedule, printable as PDF.
- **Entrepreneur View**: plain-language explanation with SWOT, risks and next steps in EN / HI / MR.
- **What-if sheet**: change inputs and re-run the engine instantly.
- **Comparison** of two or three Business Archetypes side by side.
- **Chat** about a report (tool-calling, BM25 retrieval over scheme texts) and optional **voice input** (Whisper via Groq).
- Accounts with saved reports; a seeded demo account.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python 3.12, [uv](https://docs.astral.sh/uv/), FastAPI, SQLModel, SQLite (or Postgres/Neon via `DATABASE_URL`), SSE pipeline |
| Engine | Pure Python, no I/O |
| LLM | `openai` SDK against Gemini (primary) and Groq (fallback), with `live` / `record` / `replay` cache; BM25 (`rank-bm25`) |
| Frontend | React 19, Vite, TypeScript, React Router, Tailwind, shadcn/ui, Recharts, Lucide, Mukta font, own `t()` i18n |

Mobile-first at 360 px, built for budget Android phones.

## Project structure

```
api/        FastAPI app: routes, session auth, SSE pipeline, DB, contracts.py (all API models)
engine/     Pure calculations: cost, market, schemes, finance, verdict, path_to_yes, figures
llm/        LLM client + fallback, cache, prompts, explanation, verifier, intake parser, retrieval, chat, eval
data/       Hand-curated JSON (archetypes, schemes, census, osm), scheme texts, loaders, LLM replay cache
web/        React frontend (src/types/contracts.ts is generated, never hand-edited)
fixtures/   Illustrative V1 fixtures used by contract tests (not real data)
tests/      pytest suites for engine, llm, data, verifier and API
scripts/    One-off helper scripts
docs/       PRD, TRD, architecture, API contracts, UI/UX, wireframes, ADRs, diagrams
.scratch/   Hackathon tickets, grouped by version (v1-skeleton, v2-parallel, ...)
```

## Getting started

### Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node.js 20+ and npm

### 1. Configure

```bash
cp .env.example .env
```

Fill in `GEMINI_API_KEY` and/or `GROQ_API_KEY` for LLM calls. The reply cache in `data/llm_cache/` is local and git-ignored: run once with `LLM_MODE=record`, then `LLM_MODE=replay` works offline.

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | `sqlite:///./requiem.db` by default; any SQLAlchemy URL (e.g. Neon Postgres) |
| `SESSION_SECRET` | Cookie signing secret, any long random string |
| `LLM_MODE` | `live` (always call), `record` (call and save replies), `replay` (offline, from `data/llm_cache/`) |
| `LLM_PRIMARY` | `gemini` or `groq`; the other is the fallback |
| `GEMINI_*`, `GROQ_*` | Keys, base URLs and models per provider; `GROQ_BACKUP_MODELS` are tried on rate limits |
| `GROQ_WHISPER_MODEL` | Model for voice transcription |
| `LLM_TIMEOUT_S` | Per-call timeout |
| `OSM_LIVE` | `1` = fetch competitor counts from Overpass (cached 24 h); `0` = use `data/osm/niphad_counts.json` |

### 2. Run the backend (port 8000)

```bash
uv sync
uv run uvicorn api.main:app --reload
```

On start-up it creates the tables, seeds the Niphad villages and the demo account. API docs: http://localhost:8000/docs

### 3. Run the frontend (port 5173)

```bash
cd web
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api/*` to port 8000, so there is one origin and no CORS.

**Demo login:** `sunita` / `sunita123` (four saved reports, no LLM calls needed).

## API overview

All routes sit under `/api`. Full contract: [`docs/api-contracts.md`](docs/api-contracts.md) and live OpenAPI at `/openapi.json`.

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` |
| Catalogue | `GET /localities`, `GET /archetypes`, `GET /schemes` |
| Intake | `POST /intake/parse` (free text to intake fields) |
| Reports | `POST /reports`, `GET /reports`, `GET /reports/{id}`, `GET /reports/{id}/stream` (SSE stages), `POST /reports/{id}/explanation` |
| Tools | `POST /simulate` (what-if), `POST /compare`, `POST /chat`, `POST /voice/transcribe` |

`api/contracts.py` is the single source of truth for every shape. After changing it, regenerate the frontend types:

```bash
cd web
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/contracts.ts
```

## Testing and checks

```bash
uv run pytest                 # engine, llm, data, verifier and API smoke tests
uv run python -m llm.eval     # LLM explanation eval cases
cd web && npm run check && npm run build
```

## Data

Scheme and Archetype data are hand-curated JSON in `data/`. Every Scheme rule carries a `source_url` and `verified_on`; never invent scheme figures. Helper scripts:

- `data/census_import.py`: import Census village data
- `data/osm_live.py`: fetch competitor counts from Overpass
- `data/refresh_scheme_sources.py`: re-check scheme source pages

## Contributing rules

1. **Code computes, the LLM explains.** Never let an LLM produce or change a number.
2. **`engine/` is pure Python**: no network, DB, LLM or file I/O, and every function has at least one `assert` check.
3. **LLM text never contains digits**, only `{{figure_id}}` placeholders.
4. **The API contract is frozen**: change `api/contracts.py` and the generated `contracts.ts` together.
5. **Use the domain vocabulary** in [`CONTEXT.md`](CONTEXT.md): Entrepreneur (not "user"), Own Contribution (not "capital").
6. **Secrets only in `.env`**, which is git-ignored.

## Documentation

- [`docs/prd.md`](docs/prd.md): product scope and delivery plan
- [`docs/trd.md`](docs/trd.md): technical rules and algorithms
- [`docs/architecture.md`](docs/architecture.md): components and flows ([diagram](docs/diagrams/architecture.html), [workflow](docs/diagrams/workflow.html))
- [`docs/api-contracts.md`](docs/api-contracts.md): endpoints and models
- [`docs/ui-ux.md`](docs/ui-ux.md) and [`docs/wireframes.md`](docs/wireframes.md): design system and screens
- [`CONTEXT.md`](CONTEXT.md): domain glossary
- [`docs/adr/`](docs/adr/): architecture decisions
