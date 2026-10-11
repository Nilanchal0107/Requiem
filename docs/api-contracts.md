# API Contracts

The frozen contract between `web/`, `api/`, `engine/` and `llm/`. **Source of truth in code:** `api/contracts.py` (Pydantic). `web/src/types/contracts.ts` is generated from it:

```
npx openapi-typescript http://localhost:8000/openapi.json -o web/src/types/contracts.ts
```

Frozen after V1. Changes need all three personas to agree; Fullstack edits `contracts.py`, regenerates the TS file and commits both together. Vocabulary: [`CONTEXT.md`](../CONTEXT.md).

## 1. Conventions

- Base path `/api`. JSON in and out (except `/api/voice/transcribe`, which takes multipart).
- **Money is integer rupees.** Rates are percent floats (`8.5`). Durations are months (integer).
- **Ids** are `snake_case` strings for catalogue items (`dairy`, `pmegp`). LGD codes are strings for places. Report ids are UUID strings.
- **Language** is `"en" | "hi" | "mr"`.
- **Numbers aren't formatted** by the API. `web/src/lib/format.ts` formats them per language.
- **Errors** use FastAPI's default shape: `{"detail": "<message>"}` (422 validation errors use FastAPI's list form).

| Status | When |
|---|---|
| 400 | Valid shape, but the request is invalid (e.g. unknown `archetype_id`) |
| 401 | Login required (`/api/reports` list) or bad credentials |
| 404 | Report or village not found |
| 409 | Username taken |
| 422 | Request body fails the schema |
| 502 | Both LLM providers failed and there is no cache (intake, compare summary, chat only) |

- **Auth:** a signed session cookie (`session`) set by `/api/auth/login`. No header tokens. Guests have no `user_id` in their session.

## 2. Shared models

```python
from typing import Literal
from pydantic import BaseModel, Field

Language = Literal["en", "hi", "mr"]
Source = Literal["census", "osm", "user", "assumption", "scheme", "computed"]
Unit = Literal["INR", "%", "months", "count", "ratio", "acres", "households"]
Sector = Literal["agriculture", "allied", "service", "retail", "manufacturing"]
VerdictLevel = Literal["feasible", "feasible_with_changes", "not_feasible"]


class Figure(BaseModel):
    id: str                      # placeholder key, unique within an EngineResult, e.g. "funding_gap"
    label: str                   # English label; web translates via i18n key f"figure.{id}"
    value: float                 # integer rupees when unit == "INR"
    unit: Unit
    source: Source
    formula: str | None = None   # human-readable, e.g. "project_cost − own_contribution"
    inputs: dict[str, float] | None = None
    note: str | None = None      # e.g. "OSM coverage is low in rural areas"
```

### 2.1 Places and catalogue

```python
class District(BaseModel):
    code: str
    name: str

class Block(BaseModel):
    code: str
    name: str
    district_code: str

class Village(BaseModel):
    code: str                    # LGD village code
    name: str
    block_code: str
    households: int              # Census 2011
    population: int
    is_rural: bool               # derived, never asked

class ArchetypeSummary(BaseModel):
    id: str                      # dairy | onion_cultivation | poultry | tailoring | kirana | flour_mill
    name: str
    sector: Sector
    unit_label: str              # "animals", "acres", "birds", "machines", "stock value (₹)", "capacity (kg/hr)"
    unit_scale_default: float
    unit_scale_min: float
    unit_scale_max: float
    unit_scale_step: float
    eligibility_fields: list[str]  # which Eligibility fields the form shows for this archetype

class SchemeSummary(BaseModel):
    id: str                      # mudra | pmegp | standup_india | pm_vishwakarma | cmegp | kcc
    name: str
    covers: str
    max_loan: int
    interest_rate_min: float
    interest_rate_max: float
    max_tenure_months: int
    moratorium_months: int
    subsidy: str | None          # short description, e.g. "15–35% of project cost, back-ended"
    source_url: str
    verified_on: str             # ISO date
```

### 2.2 Intake

```python
class Eligibility(BaseModel):
    age: int = Field(ge=18, le=80)
    gender: Literal["female", "male", "other"]
    social_category: Literal["general", "obc", "sc", "st"]
    education: Literal["none", "below_8th", "8th_pass", "10th_pass", "12th_pass", "graduate"]
    business_status: Literal["new", "existing"] = "new"
    prior_subsidy: bool = False
    prior_tarun_repaid: bool = False
    artisan_trade: bool = False
    farmland: Literal["none", "owned", "leased"] = "none"

class IntakeInput(BaseModel):
    village_code: str
    archetype_id: str
    unit_scale: float
    own_contribution: int = Field(ge=0)
    eligibility: Eligibility
    language: Language = "en"
    competitor_override: int | None = Field(default=None, ge=0)
    tenure_months: int | None = None   # what-if override; None = Scheme default
```

### 2.3 Engine output

```python
class MarketAnalysis(BaseModel):
    households: Figure
    potential_customers: Figure
    demand: Figure               # units per month in the archetype's revenue unit
    competitors: Figure
    competitor_capacity: Figure
    market_gap: Figure
    competitor_coverage: Literal["low", "ok"]
    channels: list[str]          # distribution channels from archetypes.json

class CostItem(BaseModel):
    name: str
    figure: Figure

class CostBreakdown(BaseModel):
    items: list[CostItem]
    project_cost: Figure

class MeansOfFinance(BaseModel):
    own_contribution: Figure
    loan: Figure
    subsidy: Figure
    subsidy_backended: bool      # True for PMEGP: subsidy does not reduce EMI
    funding_gap: Figure

class LoanTerms(BaseModel):
    principal: int
    interest_rate: float
    tenure_months: int
    moratorium_months: int
    moratorium_mode: Literal["capitalised", "serviced"]
    emi: int
    total_interest: int

class SchemeOption(BaseModel):
    scheme_id: str
    name: str
    tier: str | None = None      # e.g. "kishore" for MUDRA
    terms: LoanTerms
    effective_rate: float        # after subsidy / subvention, for ranking
    reasons: list[str]           # rules satisfied, plain English
    source_url: str

class IneligibleScheme(BaseModel):
    scheme_id: str
    name: str
    failed_rule: str             # e.g. "Project cost above ₹5,00,000 requires 8th pass"
    unlock_hint: str | None      # e.g. "₹40,000 more Own Contribution unlocks Kishore"

class SchemeMatch(BaseModel):
    best: SchemeOption | None
    alternatives: list[SchemeOption]
    ineligible: list[IneligibleScheme]

class RepaymentRow(BaseModel):
    month: int
    opening: int
    interest: int
    principal: int
    payment: int
    closing: int

class YearProjection(BaseModel):
    year: int                    # 1..5
    revenue: int
    operating_cost: int
    depreciation: int
    interest: int
    net_profit: int
    cash_flow: int
    debt_service: int
    dscr: float | None           # None when no debt service that year

class VerdictSignal(BaseModel):
    name: Literal["dscr", "market_gap", "payback", "scheme"]
    level: VerdictLevel
    figure_id: str | None

class Verdict(BaseModel):
    level: VerdictLevel          # worst of signals
    signals: list[VerdictSignal]

class Change(BaseModel):
    field: Literal["own_contribution", "unit_scale", "tenure_months"]
    from_value: float
    to_value: float
    resulting_verdict: VerdictLevel

class PathToYes(BaseModel):
    changes: list[Change]        # each change alone reaches "feasible"; empty if none found in range

class EngineResult(BaseModel):
    archetype_id: str
    village_code: str
    market: MarketAnalysis
    cost: CostBreakdown
    finance: MeansOfFinance
    schemes: SchemeMatch
    repayment: list[RepaymentRow]       # empty if no eligible Scheme
    projections: list[YearProjection]   # 5 rows
    break_even_month: Figure
    payback_months: Figure
    min_dscr: Figure
    verdict: Verdict
    path_to_yes: PathToYes | None       # None when verdict == "feasible"
    figures: dict[str, Figure]          # every Figure above, keyed by id: the placeholder registry
```

### 2.4 Explanation (Entrepreneur View)

Text contains `{{figure_id}}` placeholders. `web` replaces each one with the formatted value from `EngineResult.figures`, rendered as a Verified Figure chip with a tooltip (formula, inputs, source).

```python
class ExplanationSection(BaseModel):
    key: Literal["verdict", "market", "pricing", "risks", "path_to_yes", "next_steps"]
    title: str
    text: str                    # may contain {{figure_id}}; never raw digits

class Swot(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]
    threats: list[str]           # same placeholder rule

class Explanation(BaseModel):
    language: Language
    sections: list[ExplanationSection]
    swot: Swot
    verified: int                # placeholders that resolved to a known figure
    total: int                   # placeholders + any stripped raw-number sentences
    regenerated: bool            # True if the verifier forced one retry
    available: bool = True       # False if both LLMs failed; sections empty
```

### 2.5 Report and pipeline

```python
class Report(BaseModel):
    id: str
    status: Literal["pending", "running", "done", "failed"]
    input: IntakeInput
    engine: EngineResult | None
    explanation: Explanation | None
    created_at: str              # ISO datetime
    owner_id: int | None

class ReportSummary(BaseModel):
    id: str
    archetype_id: str
    village_name: str
    verdict: VerdictLevel | None
    created_at: str

class StageEvent(BaseModel):
    stage: Literal["intake", "market", "cost", "schemes", "dpr", "explanation"]
    status: Literal["running", "done", "retrying", "failed"]
    duration_ms: int | None = None
    sources: list[str] = []      # e.g. ["Census 2011", "OpenStreetMap", "schemes.json (verified 2026-10-01)"]
    message: str | None = None
```

## 3. Endpoints

### Auth

| Method & path | Request | Response | Notes |
|---|---|---|---|
| `POST /api/auth/register` | `{username: str (3–30), password: str (≥6)}` | `UserOut {id, username}` | 409 if taken; also logs in |
| `POST /api/auth/login` | same | `UserOut` | 401 on bad credentials |
| `POST /api/auth/logout` | — | `{ok: true}` | Clears the session |
| `GET /api/auth/me` | — | `{user: UserOut \| null}` | `null` = guest |

### Catalogue and places

| Method & path | Response |
|---|---|
| `GET /api/localities` | `District[]` |
| `GET /api/localities?district={code}` | `Block[]` |
| `GET /api/localities?district={code}&block={code}` | `Village[]` |
| `GET /api/archetypes` | `ArchetypeSummary[]` |
| `GET /api/schemes` | `SchemeSummary[]` |

### Intake

`POST /api/intake/parse`

```json
// request
{ "text": "मला निफाडमध्ये ५ म्हशींचा दुग्ध व्यवसाय सुरू करायचा आहे, माझ्याकडे १ लाख आहेत", "language": "mr" }
// response
{ "fields": { "archetype_id": "dairy", "unit_scale": 5, "own_contribution": 100000 }, "missing": ["village_code", "eligibility.age", "eligibility.social_category"] }
```

`fields` is a partial `IntakeInput` (dot paths aren't used in `fields`; it's nested JSON). `missing` lists dot paths the form must still collect.

### Reports

| Method & path | Request | Response |
|---|---|---|
| `POST /api/reports` | `IntakeInput` | `{report_id}` (status `pending`) |
| `GET /api/reports/{id}/stream` | — | `text/event-stream`, see below |
| `GET /api/reports/{id}` | — | `Report` |
| `GET /api/reports` | — | `ReportSummary[]` for the logged-in user (401 for guests) |

Guests can open any report by id. Reports are unguessable UUIDs. This is a demo app.

**SSE format** (`GET /api/reports/{id}/stream`):

```
event: stage
data: {"stage":"market","status":"running"}

event: stage
data: {"stage":"market","status":"done","duration_ms":12,"sources":["Census 2011","OpenStreetMap"]}

event: stage
data: {"stage":"explanation","status":"retrying","message":"Raw number found, regenerating"}

event: done
data: {"report_id":"5b0c..."}

event: error
data: {"detail":"..."}
```

Stages are sent in order: `intake → market → cost → schemes → dpr → explanation`. An engine failure sends `error` and sets the report to `failed`. An LLM failure still sends `done`, with `explanation.available = false`. Opening the stream on a `done` report replays the stored stage events immediately.

### What-if, Comparison, chat, voice

| Method & path | Request | Response |
|---|---|---|
| `POST /api/simulate` | `IntakeInput` | `EngineResult` (no LLM, nothing saved) |
| `POST /api/compare` | `{input: IntakeInput, archetype_ids: str[2..3]}` | `Comparison` |
| `POST /api/chat` | `ChatRequest` | `ChatResponse` |
| `POST /api/voice/transcribe` (stretch) | multipart `audio` (webm/wav), `language` | `{text: str}` |

```python
class Comparison(BaseModel):
    results: list[EngineResult]  # same order as archetype_ids; each uses its archetype's unit_scale_default
    summary: str                 # placeholders use "<archetype_id>.<figure_id>", e.g. {{dairy.min_dscr}}
    language: Language

class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    report_id: str
    message: str
    language: Language
    history: list[ChatTurn] = []   # client keeps history; last 10 turns sent

class Citation(BaseModel):
    scheme_id: str
    source_url: str
    snippet: str

class ChatResponse(BaseModel):
    reply: str                       # may contain {{figure_id}} from report figures or from `figures` below
    figures: dict[str, Figure] = {}  # extra figures produced by a simulate tool call
    citations: list[Citation] = []
    suggested_changes: list[Change] = []
    tools_used: list[Literal["get_dpr", "search_schemes", "simulate"]] = []
```

## 4. Fixture

`fixtures/report.json` is a complete `Report` for the demo persona: dairy, 5 animals, a Niphad village, ₹1,00,000 Own Contribution, female, OBC, 10th pass, language `mr`. In V1 every `GET /api/reports/{id}` returns it and the stream replays canned stage events, so `web/` can build every page before the engine exists.
