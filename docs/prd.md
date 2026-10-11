# PRD: Hyper Local Business & Loan Advisory

**Event:** Requiem Hackathon 2026, Round 2: 6 hours offline, prototype done in 5, last hour for pitch.
**Team:** 3 people (Frontend, Fullstack, AIML).
**Demo:** localhost, seeded data, Locality = Niphad block, Nashik district, Maharashtra.

Vocabulary is defined in [`CONTEXT.md`](../CONTEXT.md). The founding architecture decision is [ADR 0001](adr/0001-code-computes-llm-explains.md). Background research: [`ps-breakdown.md`](ps-breakdown.md), [`doc.md`](doc.md), [`DIFFERENTIATORS.md`](DIFFERENTIATORS.md), [`TECH_RESEARCH.md`](TECH_RESEARCH.md), [`fintech-hackathon-plan.md`](fintech-hackathon-plan.md).

---

## 1. Problem

A first-time rural Entrepreneur has a business idea but cannot answer three questions:

1. Will it work in **my** Locality?
2. How much money do I need, and how much must I borrow?
3. Which government Scheme can I get, and what will I repay?

Banks want a **DPR** (Detailed Project Report) to answer these. People pay consultants for one, and they can't read it once they have it.

## 2. Product in one line

> The Entrepreneur enters their Locality, Business Archetype, Own Contribution and a few eligibility details. The app builds a bank-format **DPR** with code, then uses GenAI to explain it in Marathi, Hindi or English.

**Pitch line:** "Other apps give advice. Ours builds the document you take to the bank, and explains every number in your language."

## 3. Goals and non-goals

**Goals**
- Cover all four PS modules: AI Business Advisor, Hyper-Local Analysis, Scheme & Loan Calculator, Feasibility Report.
- Cover all five brownie points: multilingual, chat, dashboard, what-if, Comparison.
- Every number is defensible: computed in code, tagged with a Source Badge, and checked by the verifier when it appears in AI text.
- A complete, rehearsed demo for one Locality (Niphad) and two Archetypes (dairy, onion cultivation).

**Non-goals**
- All-India coverage, live scheme scraping, more than 6 Archetypes or 6 Schemes.
- Submitting real loan applications, real OTP/SMS, payment, or KYC.
- A deployed public URL (localhost only).
- Fine-tuning, multi-agent frameworks, vector databases, low-code tools.

## 4. Users and demo persona

**Entrepreneur:** a first-time rural business owner with low financial literacy, on a phone or shared laptop, who prefers Marathi or Hindi.

**Primary demo persona:** a woman in Niphad block with about ₹1L Own Contribution who wants to start a dairy. (Being a woman matters for Stand-Up India and PMEGP's special-category rates.) The Comparison runs dairy against onion cultivation for the same person.

The exact village is fixed once the Census data is loaded.

## 5. Scope

### 5.1 Catalogue (curated JSON in `data/`)

| Business Archetype | Sector | Unit-scale knob |
|---|---|---|
| Dairy | Agri-allied | Number of animals |
| Onion cultivation | Agriculture (crop) | Acres |
| Poultry | Agri-allied | Birds |
| Tailoring | Service | Machines |
| Kirana | Retail / trade | Stock value |
| Flour mill | Manufacturing | Mill capacity |

Each archetype holds:
- cost template (line items × unit scale)
- revenue model
- operating costs
- adoption rate (households per business, or buyers per household)
- competitor capacity
- OSM tag(s)
- a short note for every assumption

| Scheme | Covers | Notes |
|---|---|---|
| MUDRA (Shishu / Kishore / Tarun / Tarun Plus) | Non-farm micro enterprises, allied activities | Tier picked by Funding Gap |
| PMEGP | New manufacturing/service units | Subsidy is **back-ended** (held as a term deposit, about 3 years) |
| Stand-Up India | SC/ST or women, greenfield | ₹10L–₹1Cr |
| PM Vishwakarma | Traditional artisans (e.g. tailors) | Concessional tranches |
| CMEGP (Maharashtra) | State employment generation | State subsidy |
| KCC | Crop cultivation | MUDRA/PMEGP don't fund pure crop farming |

Each scheme rule carries `source_url` and `verified_on`. **No public API provides scheme eligibility rules**, so this JSON is hand-curated. All figures must be re-verified before the event (see §12).

### 5.2 Locality data (pre-loaded into SQLite)

- **Census 2011** village tables for Niphad (households, population, literacy, workers), projected forward with a stated growth factor.
- **LGD codes:** district → block → village.
- **OSM competitor counts** per village per Archetype, pre-fetched and stored. They're marked low coverage, and the Entrepreneur can override them.
- Rural/urban status is **derived** from the Locality, never asked.

### 5.3 Features

**F1. Homepage** (`/`)
- Sections:
  1. Hero with pitch line and "Start your DPR" CTA
  2. The problem (three questions)
  3. How it works (pipeline visual)
  4. What makes us different
  5. Features grid
  6. Schemes covered
  7. Team
- Static content, available in EN/HI/MR.

**F2. Login** (`/login`)
- Username + password, hashed, stored in the DB. Session cookie.
- **"Continue as guest"** always visible. Guests can do everything except My Reports.

**F3. Intake** (`/new`)
- Form-first:
  - Locality picker (district → block → village)
  - Business Archetype
  - Unit scale
  - Own Contribution
  - Eligibility fields (below)
- **"Describe in your own words"** box: the LLM parses free text into form fields, and the Entrepreneur confirms them.
- Eligibility fields, shown conditionally per Archetype:

| Field | Used by |
|---|---|
| Age | PMEGP |
| Gender | Stand-Up India, PMEGP |
| Social category (Gen/OBC/SC/ST) | Stand-Up India, PMEGP |
| Education level | PMEGP |
| New or existing business | PMEGP, Stand-Up India |
| Prior government subsidy taken | PMEGP |
| Prior MUDRA Tarun loan repaid | Tarun Plus |
| Traditional artisan trade | PM Vishwakarma |
| Owns or leases farmland | KCC |

**F4. Pipeline trace**
- Submitting streams SSE stage events in order:
  1. Intake
  2. Locality market
  3. Project Cost
  4. Schemes
  5. DPR
  6. Explanation + verification
- Each event carries its status, duration and data sources. The UI lights each stage up as it completes.

**F5. Report page** (`/reports/:id`): a Verdict card above three tabs on one DPR. On mobile the tab order is Explanation (Entrepreneur View, the default), then Numbers (Dashboard), then Bank DPR; see [`ui-ux.md`](ui-ux.md) and [`wireframes.md`](wireframes.md).
- **Dashboard:**
  - Verdict
  - key numbers
  - charts: cost breakdown, means of finance, repayment, 5-year cash flow, market
  - Source Badges on every number
- **Entrepreneur View:**
  - plain-language explanation in the chosen language: Verdict, Locality market, SWOT, risks, pricing suggestions, Path to Yes, next steps
  - every figure is a Verified Figure with a tooltip showing formula, inputs and source
  - an "N/N figures verified" badge
- **Bank View:** the DPR in bank format, English, with a print stylesheet so the browser can print it to PDF. Sections:
  1. Entrepreneur profile
  2. Project summary
  3. Locality market analysis
  4. Project Cost breakdown
  5. Means of finance (Own Contribution + loan + subsidy, with PMEGP's back-ended subsidy shown correctly)
  6. Scheme terms (rate, maximum loan, tenure, moratorium)
  7. Repayment schedule
  8. 5-year projected P&L and cash flow
  9. Break-even month
  10. DSCR per year
  11. SWOT and risks
  12. Application document checklist

**F6. What-if simulator** (on the report page)
- Sliders: Own Contribution, unit scale, loan tenure.
- Debounced calls to `POST /api/simulate`. No LLM involved, target under 100 ms.
- Live updates: Project Cost, Funding Gap, matched Scheme, EMI, DSCR, Verdict.
- Highlight when a threshold flips the Scheme (e.g. Kishore → Tarun) or the Verdict.

**F7. Comparison** (`/compare`)
- 2–3 Archetypes, same Entrepreneur, Locality and Own Contribution.
- Table and one chart: Project Cost, Funding Gap, Scheme, EMI, DSCR, payback, Market Gap, Verdict.
- One short LLM paragraph on which suits the Entrepreneur.

**F8. Chat advisor** (panel on the report page)
- Tool-calling LLM, replying in the chosen language. Tools:
  - `get_dpr`
  - `search_schemes` (BM25, returns citations)
  - `simulate`
- Suggests changes but never edits the saved DPR. The Entrepreneur applies changes with the sliders.

**F9. My Reports** (`/reports`)
- Logged-in users see their saved DPRs. Opening one reloads the stored engine output with no recomputation.

**F10. Languages**
- UI strings in EN/HI/MR via i18n files, with a language switch in the header.
- The Entrepreneur View and chat are generated in the chosen language. The Bank View is always English.

**F11. Voice** (stretch)
- A mic button on the "describe" box, transcribed with Groq Whisper.

## 6. Engine rules (all deterministic, per ADR 0001)

```
Project Cost   = Σ cost-template line items × unit scale
Funding Gap    = Project Cost − Own Contribution
Loan           = Funding Gap (capped by the Scheme's maximum)
Subsidy        = Scheme % × Project Cost (PMEGP: back-ended, does not reduce EMI)
EMI            = P·r·(1+r)^n / ((1+r)^n − 1), with moratorium interest added to P or serviced, per Scheme
DSCR (year y)  = (net profit + depreciation + interest) / (principal + interest) for year y
Break-even     = first month cumulative cash flow ≥ 0
Customers      = Census households (projected) × adoption rate × reach
Market Gap     = estimated demand − competitor count × competitor capacity
```

**Scheme matching:** filter Schemes by eligibility rules, then rank by effective cost to the Entrepreneur (rate after subsidy). Return:
- the best Scheme
- the alternatives
- for each Scheme that fails, the rule it failed and what would change the result ("₹X more Own Contribution unlocks Y")

**Verdict:** the worst of these signals:

| Signal | Feasible | Feasible with changes | Not feasible |
|---|---|---|---|
| Minimum DSCR | ≥ 1.5 | 1.25 – 1.5 | < 1.25 |
| Market Gap | > 0 | ≈ 0 (within ±10% of demand) | clearly negative |
| Payback vs loan tenure | < tenure | ≤ tenure + 1 year | > tenure + 1 year |
| Eligible Scheme found | yes | — | no |

**Path to Yes:** if the Verdict isn't Feasible, goal-seek the smallest change to Own Contribution or unit scale that makes it Feasible.

**Source Badge:** every number in the engine output carries `source` ∈ {`census`, `osm`, `user`, `assumption`, `scheme`, `computed`} plus a `formula` string where computed.

## 7. Where the LLM is used

| Use | Model | Guardrail |
|---|---|---|
| Parse free text into intake fields | Gemini, Groq fallback | JSON schema validation; the Entrepreneur confirms fields |
| Entrepreneur View | Gemini, Groq fallback | Gets engine JSON only; the **verifier** extracts every number from the text and compares it with engine values; on mismatch, regenerate once, then flag unmatched figures |
| Comparison paragraph | Gemini, Groq fallback | Same verifier |
| Chat advisor | Gemini, Groq fallback | Tools only; cannot write to the DPR |
| Voice (stretch) | Groq Whisper | — |

Temperature 0.2–0.4 for report text. Cached responses for the scripted demo inputs serve as an offline fallback.

## 8. Architecture

```
web/  (React + Vite + TS + React Router + Tailwind + Recharts + i18n)
  │  REST + SSE
api/  (FastAPI + SQLModel)  ── auth, routes, SSE streaming, persistence
  │  imports
engine/ (pure Python, no I/O)  ── cost, market, schemes, finance, verdict, path-to-yes
llm/    (Python)               ── Gemini/Groq client, prompts, verifier, BM25, chat tools
data/                          ── archetypes.json, schemes.json, scheme_texts/, seed scripts
DB: SQLite (DATABASE_URL can point to Neon Postgres; tested once in V3)
```

**DB tables:**
- `user`
- `report`: inputs plus the full engine output and LLM text as JSON, owner (nullable for guests), created_at
- `village`: Census + LGD + OSM counts

Schemes and Archetypes stay in JSON (hand-reviewed, versioned in git).

### 8.1 API contract (frozen in V1)

Summary only. The full request/response shapes are in [`api-contracts.md`](api-contracts.md), technical rules in [`trd.md`](trd.md), and components and flows in [`architecture.md`](architecture.md).

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create user |
| POST | `/api/auth/login` | Start session |
| POST | `/api/auth/logout` | End session |
| GET | `/api/auth/me` | Current user or guest |
| GET | `/api/localities` | Districts → blocks → villages (query: `district`, `block`) |
| GET | `/api/archetypes` | Catalogue with unit-scale knobs and required eligibility fields |
| GET | `/api/schemes` | Scheme list with terms and sources |
| POST | `/api/intake/parse` | Free text → partial `IntakeInput` |
| POST | `/api/reports` | `IntakeInput` → `{report_id}` (status pending) |
| GET | `/api/reports/{id}/stream` | SSE stream of `StageEvent`s; runs the pipeline; final `done` event |
| GET | `/api/reports` | Current user's saved reports |
| GET | `/api/reports/{id}` | Full `Report` |
| POST | `/api/simulate` | `IntakeInput` (+ overrides) → `EngineResult` (no LLM) |
| POST | `/api/compare` | `IntakeInput` + archetype ids → `Comparison` |
| POST | `/api/chat` | `{report_id, message, language}` → reply + citations |
| POST | `/api/voice/transcribe` | Audio → text (stretch) |

**Core models**, defined once in `api/contracts.py`; `web/src/types/contracts.ts` is generated from OpenAPI:
- `IntakeInput`: locality ids, archetype id, unit scale, own contribution, eligibility fields, language, competitor override
- `Figure`: `{value, unit, source, formula?, inputs?}`
- `MarketAnalysis`, `CostBreakdown`, `SchemeMatch` (best, alternatives, failed rules with unlock hints), `LoanTerms`, `RepaymentRow[]`, `YearProjection[]`, `Verdict`, `PathToYes`
- `EngineResult`: all of the above, made of `Figure`s
- `Explanation`: Entrepreneur View text sections + `verified: n/total` + unmatched figures
- `Report`: `{id, input, engine: EngineResult, explanation, created_at}`
- `StageEvent`: `{stage, status, duration_ms, sources[], payload?}`
- `Comparison`: `EngineResult[]` + paragraph

A sample `fixtures/report.json` is committed in V1 so the frontend can build without the backend.

### 8.2 Routes

| Route | Page | Auth |
|---|---|---|
| `/` | Homepage | Public |
| `/login` | Login / register / guest | Public |
| `/new` | Intake + pipeline trace | Guest ok |
| `/reports/:id` | Dashboard · Entrepreneur View · Bank View · what-if · chat | Guest ok |
| `/compare` | Comparison | Guest ok |
| `/reports` | My Reports | Logged in |

## 9. Team, ownership and rules

| Persona | Owns (only they edit) | Delivers |
|---|---|---|
| **Frontend** | `web/` (except `web/src/types/contracts.ts`) | Homepage, design system, all pages, charts, i18n, print stylesheet |
| **Fullstack** | `api/`, `web/src/types/contracts.ts`, `fixtures/`, DB, auth | Skeleton, contract, routes, SSE, persistence, integration |
| **AIML** | `engine/`, `llm/`, `data/` | Catalogue JSON, Locality seed, engine, verifier, prompts, BM25, chat tools |

**Rules**
1. **The contract is frozen after V1.** Any change to `contracts.py` needs all three to agree. Fullstack edits it, regenerates `contracts.ts` with `openapi-typescript`, and commits both together.
2. **Never edit outside your folder.** If you need something from another folder, ask the owner.
3. **`engine/` is pure.** No network, DB or LLM. Every function has at least one `assert` check.
4. **No LLM arithmetic** (ADR 0001). The LLM receives engine output and never produces a number that isn't in it.
5. **Everyone uses the vocabulary in `CONTEXT.md`** in code, UI copy and commits.
6. Small commits, one ticket each, pull before you push.
7. Secrets only in `.env` (git-ignored). `.env.example` is committed.

## 10. Delivery plan

Tickets live in `.scratch/<version>/issues/NN-<slug>.md` (see `docs/agents/issue-tracker.md`). Each has an owner persona and a `Blocked by:` line.

| Version | Time | Goal | Exit criteria |
|---|---|---|---|
| **Prep** (before event) | — | Docs, verified scheme figures, Niphad Census + OSM data downloaded | PRD, CONTEXT, ADR committed; data files ready |
| **V1: Skeleton** | 0:00–0:45 | Fullstack scaffolds `api/` + `web/`, DB, routing, auth stub, **frozen contract**, fixture, every endpoint returning fixture data. In parallel: AIML starts `data/` + `engine/`; Frontend starts homepage + design system. | `npm run dev` + `uvicorn` both run; every route renders; every endpoint responds with contract-shaped data |
| **V2: Parallel build** | 0:45–3:45 | Each persona works through their own tickets against the contract and fixture | Each persona's tickets pass their checks in isolation |
| **V3: Merge** | 3:45–4:45 | Replace fixtures with the real engine + LLM; end-to-end demo path; Neon switch check; demo cache | The scripted demo runs end to end twice on localhost |
| **Buffer** | 4:45–5:00 | Fixes only | — |
| **Pitch** | 5:00–6:00 | Slides, rehearsal | — |

**Cut order if behind** (first to go first):
1. Voice
2. Chat tools beyond `get_dpr`
3. Comparison
4. Translated homepage copy

**Protected:** DPR (Bank View), Entrepreneur View + verifier, what-if, Verdict.

## 11. Success criteria

- The scripted demo (dairy in Niphad, then a what-if that flips the Scheme, then the Comparison with onion cultivation, then the Bank View PDF, then a Marathi Entrepreneur View) runs end to end without network access using cached LLM responses.
- 100% of numbers in the Entrepreneur View are Verified Figures for the demo inputs.
- **Eval set:** 15 cases (5 Archetypes × 3 Niphad villages), each with a hand-labelled correct Scheme. Report scheme-match accuracy and verifier pass rate in the pitch.
- `/api/simulate` responds in under 100 ms. The full report pipeline finishes in under 20 s.

## 12. Risks and pre-event checks

| Risk | Mitigation |
|---|---|
| Scheme figures out of date | Re-verify every rule before the event (PMEGP FY26-27 status, MUDRA Tarun Plus, KCC subvention limit after Budget 2025, CMEGP terms, PM Vishwakarma tranches); show `verified_on` in the UI |
| Venue wifi or LLM quota | Groq fallback; cached demo responses; SQLite local; no runtime OSM calls |
| Thin OSM coverage | "Low coverage" badge + user override |
| Team new to parallel work | Contract-first V1, strict folder ownership, fixture-driven frontend |
| Rule: "pre-built projects not allowed" | Only docs and public data are prepared beforehand; all code written during the event. Confirm with organisers in Q&A. |
| Advice liability | "Indicative assessment, verify with your bank" note on every view |

## 13. Open questions for organiser Q&A

1. Is preparing public datasets (Census, scheme figures) before the event allowed?
2. Is any market or scheme data supplied?
3. Any API or wifi restrictions at the venue?
4. Is a local demo acceptable? (Assumed yes.)
