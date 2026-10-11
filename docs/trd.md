# TRD: Technical Requirements

How the product in [`prd.md`](prd.md) is built. Component layout and flows: [`architecture.md`](architecture.md). Endpoints and models: [`api-contracts.md`](api-contracts.md). Vocabulary: [`CONTEXT.md`](../CONTEXT.md). Founding rule: [ADR 0001](adr/0001-code-computes-llm-explains.md), so code computes every number and the LLM only explains.

---

## 1. Stack and toolchain

| Layer | Choice | Notes |
|---|---|---|
| Python | **3.12**, pinned via `.python-version` | `uv` installs it automatically on every laptop |
| Python packages | **uv**, one project at the repo root | `uv sync`; the lockfile pins versions |
| API | **FastAPI** + **SQLModel** + Starlette `SessionMiddleware` | `uv run uvicorn api.main:app --reload` |
| DB | **SQLite** (`sqlite:///./requiem.db`) | `DATABASE_URL` can point to Neon Postgres |
| Password hashing | **`hashlib.scrypt`** (stdlib) | No bcrypt/passlib |
| LLM | **`openai` Python SDK** against Gemini and Groq OpenAI-compatible endpoints | One client, provider switch |
| Retrieval | **`rank-bm25`** | BM25 only, no embeddings |
| Tests | **pytest** | `engine/` + API smoke test |
| Node | **≥ 20**, **npm** | |
| Frontend | **React + Vite + TypeScript**, **React Router** (`createBrowserRouter`), **Tailwind** (`@tailwindcss/vite`), **shadcn/ui**, **Recharts** | |
| Contract types | **`openapi-typescript`** (run with npx) | Generates `web/src/types/contracts.ts` |
| i18n | Own `t()` over `en.json` / `hi.json` / `mr.json` | No i18n library |
| Font | **Mukta** via `@fontsource/mukta` (400/500/600/700) | Latin + Devanagari, self-hosted so it works offline |
| Icons | **Lucide** (`lucide-react`, comes with shadcn/ui) | No emoji icons |
| Design | Mobile-first; tokens and components in [`ui-ux.md`](ui-ux.md), screens in [`wireframes.md`](wireframes.md) | |
| Number formatting | **`Intl.NumberFormat`** (browser native) | §8 |
| PDF | Browser print + `@media print` stylesheet | No PDF library |

**Python dependencies (complete list):** `fastapi`, `uvicorn[standard]`, `sqlmodel`, `itsdangerous` (needed by SessionMiddleware), `python-multipart` (voice upload), `openai`, `rank-bm25`, `python-dotenv`, and `pytest` as a dev dependency. Adding anything else needs a reason in the ticket.

## 2. Non-functional requirements

| Requirement | Target |
|---|---|
| `/api/simulate` latency | < 100 ms on a laptop |
| Report pipeline, live LLM | < 20 s end to end; first stage event < 1 s |
| Report pipeline, `LLM_MODE=replay` | < 2 s |
| Offline demo | Fully works with `LLM_MODE=replay` and no network |
| Screen sizes | Usable at 360 px wide; desktop is the primary demo |
| Accessibility | WCAG AA contrast, keyboard reachable controls, labels on every input, colour never the only signal (Verdict also has text and an icon) |
| Languages | UI strings, Entrepreneur View and chat in EN/HI/MR; Bank View in English |
| Correctness | 100% of figures in LLM text come from placeholders (§6.3) |
| Security | Passwords scrypt-hashed; signed session cookie; secrets only in `.env`; no user input placed in raw SQL (SQLModel only) |

## 3. Environment variables (`.env.example`)

```
DATABASE_URL=sqlite:///./requiem.db
SESSION_SECRET=change-me
LLM_MODE=live                 # live | record | replay
LLM_PRIMARY=gemini            # gemini | groq
GEMINI_API_KEY=
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=                 # set on the day after checking current free-tier models
GROQ_API_KEY=
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=                   # set on the day
GROQ_WHISPER_MODEL=           # stretch: voice
LLM_TIMEOUT_S=15
```

## 4. Data

### 4.1 `data/archetypes.json`

A list of archetype objects. All numbers are **assumptions** with a `note`, and their Source Badge is `assumption`. The values below are illustrative; AIML fills in the real ones with notes.

```json
{
  "id": "dairy",
  "name": "Dairy",
  "sector": "allied",
  "unit_label": "animals",
  "unit_scale": { "default": 5, "min": 2, "max": 20, "step": 1 },
  "eligibility_fields": ["age", "gender", "social_category", "education", "business_status", "prior_subsidy", "prior_tarun_repaid"],
  "cost_items": [
    { "id": "animals", "name": "Buffaloes", "fixed": 0, "per_unit": 70000, "depreciation_pct": 0, "note": "..." },
    { "id": "shed", "name": "Cattle shed", "fixed": 60000, "per_unit": 10000, "depreciation_pct": 10, "note": "..." }
  ],
  "working_capital_months": 2,
  "revenue": { "unit": "litres", "output_per_unit_per_month": 240, "price": 45, "note": "..." },
  "operating_cost": { "variable_pct_of_revenue": 55, "fixed_monthly": 2000, "note": "..." },
  "ramp_up_months": 3,
  "target_utilisation_pct": 90,
  "growth_pct_per_year": 5,
  "market": {
    "mode": "aggregator",
    "aggregator": "Cooperative milk collection centre",
    "adoption_rate": null,
    "units_per_customer_per_month": null,
    "competitor_osm_tags": [],
    "capacity_per_competitor": null
  },
  "channels": ["Cooperative collection centre", "Direct to households", "Sweet shops"]
}
```

**Market modes**
- **`local`** (tailoring, kirana, flour mill, poultry if it sells locally): demand comes from Locality households and competes with local competitors (§5.2).
- **`aggregator`** (dairy, onion cultivation): output is sold to a cooperative or APMC (Lasalgaon for onion), so local household demand doesn't limit sales. The Market Gap signal is replaced by "aggregator within reach" and shown with a note. Without this distinction, a dairy with no local milk buyers would wrongly come out "Not feasible".

### 4.2 `data/schemes.json`

A list of Scheme objects. **Every number must be verified against `source_url` before the event; `verified_on` is the date it was checked.** Example shape (values illustrative):

```json
{
  "id": "pmegp",
  "name": "PMEGP",
  "covers": "New manufacturing and service units",
  "sectors": ["allied", "service", "retail", "manufacturing"],
  "source_url": "https://www.kviconline.gov.in/pmegpeportal/",
  "verified_on": "2026-10-__",
  "rules": [
    { "field": "eligibility.age", "op": "gte", "value": 18, "message": "Applicant must be 18 or older" },
    { "field": "eligibility.business_status", "op": "eq", "value": "new", "message": "Only new units qualify" },
    { "field": "eligibility.prior_subsidy", "op": "eq", "value": false, "message": "No earlier government subsidy for the same unit" },
    { "field": "project_cost", "op": "lte", "value": 2000000, "when": [{ "field": "sector", "op": "in", "value": ["service", "retail"] }], "message": "Service projects up to ₹20 lakh" },
    { "field": "eligibility.education", "op": "in", "value": ["8th_pass", "10th_pass", "12th_pass", "graduate"], "when": [{ "field": "project_cost", "op": "gt", "value": 500000 }], "message": "8th pass required above ₹5 lakh (service)" }
  ],
  "own_contribution_pct": [
    { "pct": 5, "when": [{ "field": "special_category", "op": "eq", "value": true }] },
    { "pct": 10 }
  ],
  "loan": { "max": 4750000, "interest_rate": 10.0, "rate_source": "assumption", "max_tenure_months": 84, "moratorium_months": 6, "moratorium_mode": "serviced", "repayment_mode": "emi" },
  "tiers": [],
  "subsidy": {
    "type": "capital_backended",
    "lock_in_months": 36,
    "rates": [
      { "pct": 35, "when": [{ "field": "special_category", "op": "eq", "value": true }, { "field": "is_rural", "op": "eq", "value": true }] },
      { "pct": 25, "when": [{ "field": "is_rural", "op": "eq", "value": true }] },
      { "pct": 15 }
    ]
  }
}
```

**Rule language**
- **Rule:** `{field, op, value, when?, message}`.
- **`op`:** `eq`, `ne`, `in`, `not_in`, `gt`, `gte`, `lt`, `lte`.
- **`when`:** a list of conditions, all of which must hold for the rule to apply.
- **Addressable fields:**
  - every `IntakeInput` field, using dot paths into `eligibility`
  - derived values: `project_cost`, `funding_gap`, `own_contribution_pct`, `sector`, `is_rural`, `archetype_id`
  - `special_category`: true if SC/ST/OBC, woman, or similar, as the Scheme defines it
- **Lists:** `own_contribution_pct` and `subsidy.rates` take the **first** entry whose `when` matches.
- **Tiers:** MUDRA uses `tiers: [{id, name, max_loan, when?}]` (Shishu / Kishore / Tarun / Tarun Plus, where Tarun Plus requires `prior_tarun_repaid`). The engine picks the smallest tier that covers the loan.
- **`subsidy.type`:**
  - `none`
  - `capital_backended` (PMEGP)
  - `capital_upfront`: reduces the loan
  - `interest_subvention`: reduces `effective_rate`, e.g. KCC prompt-repayment incentive
- **`repayment_mode`:** `emi`, or `bullet` (KCC: principal plus interest repaid once at harvest, at the end of the tenure).
- **Interest rates:** banks set the actual rate for most schemes. The JSON holds a typical rate with `rate_source: "assumption"` unless the scheme fixes it (e.g. PM Vishwakarma).

### 4.3 `data/scheme_texts/<scheme_id>.md`

Official wording, copied from the source page, used for BM25 citations. Front matter holds `scheme_id` and `source_url`, and `##` headings split it into chunks.

### 4.4 Locality source files and seed

- **`data/census/`:** Census 2011 village tables for Niphad block (LGD village code, name, households, population, literacy, workers).
- **`data/osm/niphad_counts.json`:** `{village_code: {archetype_id: count}}`, pre-fetched from Overpass using each archetype's `competitor_osm_tags` within its reach radius.
- **`data/seed.py`:** loads both into the `village` table. It's idempotent, so running it twice is safe.

### 4.5 DB tables (SQLModel)

| Table | Columns |
|---|---|
| `user` | `id` int PK · `username` unique · `password_hash` (`scrypt$<salt hex>$<hash hex>`) · `created_at` |
| `report` | `id` str PK (uuid4) · `owner_id` FK nullable · `status` · `input` JSON · `engine` JSON nullable · `explanation` JSON nullable · `stages` JSON (list of `StageEvent`, used for replay) · `created_at` |
| `village` | `code` PK · `name` · `block_code` · `block_name` · `district_code` · `district_name` · `households` · `population` · `literacy_rate` · `workers` · `is_rural` · `osm_counts` JSON |

Tables are created with `SQLModel.metadata.create_all` at startup. No migrations; delete the DB file to reset it.

## 5. Engine (pure Python)

The entry point is `engine.run_engine(input, archetype, schemes, village, *, with_path_to_yes=True) -> EngineResult`. All inputs are plain dicts or contract models passed in by the caller. Every helper is a pure function.

### 5.1 Cost

```
cost item value  = fixed + per_unit × unit_scale
working capital  = working_capital_months × monthly operating cost at target utilisation
project_cost     = Σ cost items + working capital
```

### 5.2 Market

```
households_now      = census_households × (1 + 0.012)^(current_year − 2011)          [assumption: growth 1.2 %/yr]
our_capacity        = unit_scale × output_per_unit_per_month
local mode:
  potential_customers = households_now × adoption_rate
  demand              = potential_customers × units_per_customer_per_month
  competitors         = competitor_override ?? osm_counts[archetype]                   [source: user | osm]
  competitor_capacity = competitors × capacity_per_competitor
  market_gap          = demand − competitor_capacity
  sales_ceiling       = max(market_gap, 0.3 × our_capacity)                            [assumption: 30 % share is winnable]
aggregator mode:
  market_gap figure is not produced; sales_ceiling = our_capacity
competitor_coverage = "low" when the OSM count is 0 and there's no override
```

### 5.3 Revenue and operating cost (monthly, 60 months)

```
utilisation(m) = target_utilisation × min(1, m / ramp_up_months)
units(m)       = min(our_capacity × utilisation(m), sales_ceiling) × (1 + growth)^(year(m) − 1)
revenue(m)     = units(m) × price
opex(m)        = revenue(m) × variable_pct + fixed_monthly
```

### 5.4 Scheme matching

1. For each Scheme whose `sectors` include the archetype's sector, evaluate `rules`. The first failed rule makes it ineligible, and the `message` becomes `failed_rule`.
2. Check Own Contribution: `own_contribution ≥ pct × project_cost`.
3. Loan sizing:
   - `principal = funding_gap`, reduced by subsidy only when the subsidy type is `capital_upfront`.
   - If `principal > max` (or the largest tier), the Scheme is ineligible.
4. **Unlock hint:** for a failure on a numeric threshold, compute the change needed. Examples: "₹X more Own Contribution", "reduce the project to N units", "8th pass required above ₹5 lakh".
5. Rank eligible options by `effective_rate`: the rate minus interest subvention, minus the annualised value of a capital subsidy over the tenure. Lowest first. `best` is the first.

### 5.5 Loan and repayment

```
r = annual_rate / 12 / 100;  n = tenure_months − moratorium_months
moratorium capitalised: P' = P × (1 + r)^moratorium;  pay 0 during moratorium
moratorium serviced:    pay P × r each moratorium month;  P' = P
EMI = P'·r·(1+r)^n / ((1+r)^n − 1)       (r = 0 → P'/n)
bullet (KCC): one payment of P × (1 + r)^tenure at month tenure
PMEGP back-ended subsidy: at month lock_in_months, outstanding principal −= subsidy, then EMI is recomputed over the remaining months
Rounding: round to whole rupees per row; the final row absorbs the remainder so the closing balance is exactly 0
```

### 5.6 Projections, DSCR, break-even, payback

```
depreciation (yearly) = Σ cost_item value × depreciation_pct            straight line
interest_y, principal_y from the repayment schedule
net_profit_y   = revenue_y − opex_y − depreciation_y − interest_y        [tax ignored: assumption, micro enterprise]
cash_flow_y    = net_profit_y + depreciation_y − principal_y
debt_service_y = principal_y + interest_y
DSCR_y         = (net_profit_y + depreciation_y + interest_y) / debt_service_y     (None if debt_service_y = 0)
min_dscr       = min over years with debt service
break_even_month = first month with revenue(m) − opex(m) − payment(m) ≥ 0
payback_months   = first month where Σ (revenue − opex) ≥ project_cost; 999 if not within 60 months
```

### 5.7 Verdict

| Signal | Feasible | Feasible with changes | Not feasible |
|---|---|---|---|
| `dscr` (min_dscr) | ≥ 1.5 | ≥ 1.25 | < 1.25 |
| `market_gap` (local mode only) | gap > 10% of demand | within ±10% of demand | gap < −10% of demand |
| `payback` | ≤ loan tenure | ≤ tenure + 12 months | longer |
| `scheme` | best exists | — | none eligible |

`level` is the worst signal level.

### 5.8 Path to Yes

Runs only when the Verdict isn't `feasible`, and calls `run_engine(..., with_path_to_yes=False)`.

- **Own Contribution:** raise in ₹5,000 steps up to `project_cost`. Return the first value that is `feasible`.
- **Unit scale:** lower by `step` down to `min`. Return the first value that is `feasible`.
- **Tenure:** try the best Scheme's maximum tenure.

Return every change that reaches `feasible` on its own. At most about 250 engine runs, well under 100 ms.

### 5.9 Figure ids (the placeholder registry)

`households`, `potential_customers`, `demand`, `competitors`, `competitor_capacity`, `market_gap`, `our_capacity`, `project_cost`, `cost.<item_id>`, `working_capital`, `own_contribution`, `funding_gap`, `loan`, `subsidy`, `interest_rate`, `tenure_months`, `moratorium_months`, `emi`, `total_interest`, `year1_revenue`, `year1_net_profit`, `monthly_profit`, `break_even_month`, `payback_months`, `min_dscr`.

Every `Figure` built anywhere in the engine is added to `EngineResult.figures`. Ids must be unique.

## 6. LLM layer

### 6.1 Client (`llm/client.py`)

- `complete(messages, *, tools=None, json=False) -> response`, using the `openai` SDK with `base_url`, `api_key` and `model` from env for `LLM_PRIMARY`.
- On an exception or after `LLM_TIMEOUT_S`, retry once on the other provider.
- Temperature: 0.3 for explanations, 0 for intake parsing.
- `json=True` sets `response_format={"type": "json_object"}`. The result is validated with Pydantic, with one retry on validation failure (the error is sent back to the model).

### 6.2 Cache (`llm/cache.py`)

- Key: `sha256(model + json(messages) + json(tools))`.
- `record` calls the provider and writes `data/llm_cache/<key>.json`.
- `replay` reads only and raises if the key is missing.
- `live` ignores the cache.
- Cache files are committed so the demo laptop has them.

### 6.3 Entrepreneur View and the verifier (`llm/explain.py`, `llm/verifier.py`)

**Prompt input:** `EngineResult` without repayment rows, plus a table of `figure_id | label | value | unit` and the language.

**Instructions to the model:**
- Return `Explanation` JSON: sections + SWOT.
- Write in the requested language, simply, for a first-time entrepreneur.
- **Every number must be written as `{{figure_id}}` from the table. Never write digits.**
- Don't decide the Verdict. Explain the one given.

**Verifier:**
1. Find placeholders with `\{\{([a-z0-9_.]+)\}\}`. Each id must exist in `figures` (or, in Comparison, `<archetype_id>.<figure_id>`).
2. Remove the placeholders, then search for digits with `[0-9०-९]` (ASCII and Devanagari).
3. If an unknown id or a raw digit is found:
   - regenerate once, telling the model which sentences broke the rule
   - emit a `retrying` stage event
   - set `regenerated = true`
4. If it still fails, strip the offending sentences.
5. `verified` = valid placeholders. `total` = `verified` + stripped sentences.

Known gap: numbers written as words ("पाच", "five") aren't detected. The prompt forbids them; accept the residual risk.

### 6.4 Intake parsing (`llm/intake.py`)

The model gets free text, the archetype id list and the language, and returns a partial `IntakeInput` as JSON. This is extraction of the Entrepreneur's own input (e.g. "१ लाख" becomes 100000), which the Entrepreneur confirms in the form, so it doesn't break ADR 0001. Unknown archetypes are dropped. `missing` is computed in code, not by the LLM.

### 6.5 Chat (`llm/chat.py`)

- The system prompt holds a report summary, the figure table, the placeholder rule and the language.
- Tools:
  - `get_dpr(section)`: returns that part of the stored `EngineResult`
  - `search_schemes(query_in_english)`: BM25 top 3 chunks, returned as citations
  - `simulate(changes)`: runs `run_engine` with the changes applied; new figures are added to the response under ids prefixed `sim.`
- At most 3 tool rounds, then the verifier runs on the reply.
- `simulate` results also become `suggested_changes`.

### 6.6 Retrieval (`llm/retrieval.py`)

At startup, chunk `scheme_texts/*.md` by `##` heading and tokenise with lowercase `\w+`. Index them in memory with `BM25Okapi` and return the top 3 chunks with `scheme_id`, `source_url` and a snippet. The corpus is English; the chat model translates the query when it calls the tool.

### 6.7 Eval (`llm/eval.py`)

`uv run python -m llm.eval` runs 15 cases from `data/eval_cases.json` (5 archetypes × 3 Niphad villages, each with a hand-labelled `expected_scheme`). It prints scheme-match accuracy and the verifier pass rate. These are the numbers for the pitch.

## 7. API implementation notes

- `api/main.py`:
  - `SessionMiddleware(secret_key=SESSION_SECRET, same_site="lax")`
  - routers under `/api`
  - startup: `create_all`, load the catalogue and build the BM25 index once, kept in module state
- `current_user` dependency: reads `session["user_id"]` and returns a `User` or `None`. `require_user` raises 401.
- The SSE stream uses `StreamingResponse(media_type="text/event-stream")` with a generator from `api/pipeline.py`. Each stage event is appended to `report.stages` and saved, so a reconnect can replay it.
- During V1–V2, `catalog`, `reports` and `simulate` routes return fixture data behind a `USE_FIXTURES` flag in `api/main.py`. Remove the flag in V3.

## 8. Frontend implementation notes

- **`vite.config.ts`:** `server.proxy = { "/api": "http://localhost:8000" }`.
- **`src/api.ts`:** a `request<T>(path, init)` wrapper over `fetch` with `credentials: "include"`. It throws `{status, detail}` on a non-2xx response. Types come only from `types/contracts.ts`.
- **`src/lib/format.ts`:**
  - `formatFigure(f: Figure, lang)` uses `Intl.NumberFormat` with locale `en-IN` / `hi-IN` / `mr-IN`
  - INR: `{style: "currency", currency: "INR", maximumFractionDigits: 0}`
  - Devanagari digits for `hi`/`mr` in the Entrepreneur View via the `-u-nu-deva` locale extension
  - the Bank View always uses `en-IN`
- **Placeholder rendering:** split text on `{{id}}` and render a `<FigureChip>` (formatted value + tooltip with formula, inputs and `<SourceBadge>`) for each id.
- **i18n:** `t(key)` looks up the current language's JSON and falls back to `en`. The language is stored in `localStorage` (wrapped in try/catch).
- **What-if:** slider changes are debounced by 250 ms before `POST /api/simulate`. Diff `schemes.best.scheme_id`, `schemes.best.tier` and `verdict.level` against the saved report and highlight changes.
- **Print:** an `@media print` block on the Bank View hides the navigation, tabs and sliders, and forces a light theme and A4 page breaks between sections.

## 9. Testing

| Suite | Command | Must cover |
|---|---|---|
| Engine | `uv run pytest tests/engine` | EMI against a hand-checked bank calculator value; capitalised vs serviced moratorium; PMEGP back-ended subsidy changes the outstanding balance at month 36 and not before; MUDRA tier pick at each boundary (₹50,000 / ₹5,00,000 / ₹10,00,000); Own Contribution % failure produces an unlock hint; KCC bullet repayment; Verdict worst-of; Path to Yes returns a change that really reaches `feasible`; repayment schedule closes at exactly 0 |
| Verifier | `uv run pytest tests/test_verifier.py` | Accepts placeholders; rejects ASCII and Devanagari digits; rejects unknown ids |
| API smoke | `uv run pytest tests/test_api_smoke.py` | Every endpoint returns a contract-valid response (FastAPI `TestClient`, `LLM_MODE=replay`) |
| Eval | `uv run python -m llm.eval` | §6.7 |

No frontend tests. The demo script, run twice in V3, is the end-to-end test.

## 10. Conventions

- Use `CONTEXT.md` terms in identifiers and copy: `own_contribution`, not `capital`; `entrepreneur`, not `user`. The exception is the `user` table, which is about login.
- Python: `snake_case`, type hints on public functions. TypeScript: generated contract types keep their `snake_case` fields; don't remap them.
- One ticket per commit: `V2-07: scheme tier selection`.
- Never edit outside your persona's folders (see `CLAUDE.md`).

## 11. Setup (any laptop)

```
uv sync
cp .env.example .env            # fill keys
uv run python -m data.seed
uv run uvicorn api.main:app --reload
cd web && npm install && npm run dev
npx openapi-typescript http://localhost:8000/openapi.json -o web/src/types/contracts.ts   # after any contract change
```
