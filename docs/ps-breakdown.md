# PS Breakdown: Hyper Local Business & Loan Advisory

## 1. What they're really asking for

Strip away the wording and the brief asks for three engines feeding one output:

| Engine | Input | Output | What kind of problem it is |
|---|---|---|---|
| **Market engine** | Location + business idea | Demand, customers, competitors, gaps | Data problem, the hardest part |
| **Finance engine** | Capital + project cost | Funding gap, matching schemes, EMI schedule | Rules and math, deterministic |
| **Advisor engine** | Everything above | SWOT, pricing, risks, recommendations, report | Synthesis, where GenAI fits best |

**The trap:** most teams will build a ChatGPT wrapper that writes a nice-sounding report. Judges will see dozens of those. The phrase that separates winners is *"rather than relying on assumptions or generic business advice"*. They are telling you that hallucinated numbers fail the brief.

## 2. Who the user is (and the design constraints that follow)

- **First-time rural entrepreneur.** Low financial literacy, probably on a phone, may prefer voice or their own language.
- **Typical ideas:** dairy, poultry, goatery, kirana store, tailoring, flour mill, mobile repair, beauty parlour, food processing.
- **Typical capital:** ₹20k to ₹5L. The loans they need mostly fall in Mudra Shishu/Kishore (under ₹5L) or PMEGP territory.
- **The Marathi requirement tells you the judges are probably thinking about Maharashtra.** Build your demo data around a real Maharashtra district.

## 3. Requirement decomposition

**Must-haves (graded):**
1. Conversational advisor: feasibility, SWOT, pricing, next steps, all specific to the location
2. Hyper-local analysis at village, block or district level: customer count, demand, competitors, distribution channels, gaps
3. Finance:
   - project cost estimate
   - gap = cost − own capital
   - scheme matching against eligibility
   - interest rate, maximum loan, tenure, moratorium
   - repayment schedule
4. Single feasibility report, downloadable or shareable

**Brownie points, ranked by return on effort:**

| Feature | Effort | Demo impact | Verdict |
|---|---|---|---|
| What-if simulator | Low (it's just sliders on the finance engine) | High | **Do it** |
| Visual dashboard | Low to medium | High | **Do it** |
| Multilingual (Hindi/Marathi) | Low (the LLM handles it, plus UI string files) | High with these judges | **Do it** |
| Chat interface | Already required | — | Free |
| Business comparison | Medium (run the pipeline N times, show a table) | Medium | Do it if time allows |

## 4. The hard problem: hyper-local data

This is where you win or lose. An LLM does not know how many dairies operate in Shirur block. You need real data sources, combined with honest estimation.

| Signal | Source | Notes |
|---|---|---|
| Population, households, literacy, occupation | **Census 2011 village directory / PCA** (data.gov.in) | Old but granular to village level. Project it forward with a growth factor. |
| Admin hierarchy (village → block → district) | **LGD (Local Government Directory)** codes | Clean dropdowns, no free-text location |
| Existing competitors | **OpenStreetMap Overpass API** (free) or Google Places (paid, better rural coverage) | Count shops of type X within N km |
| Sector credit potential per district | **NABARD Potential Linked Credit Plans (PLP)** | **Hidden gem.** District-wise documents estimating credit potential by sector (dairy, poultry, MSME). Almost nobody will use these. |
| Agri / commodity prices | **Agmarknet** | For dairy, poultry and agro-processing pricing |
| Livestock density | Livestock Census | For dairy and goatery feasibility |
| Banks / branches nearby | RBI bank branch data | Matters for "where to apply" |

**Recommended approach:** pre-load data for one or two districts so the demo works end to end. Then use a transparent heuristic for demand:

> potential customers = households × adoption rate for the category × reachable radius
> market gap = estimated demand − competitor capacity

Show the formula and give each number a confidence badge: "Census data", "Estimated", or "AI assumption". That honesty reads as maturity to judges.

## 5. Finance engine: where the depth shows

**Keep the LLM out of the math.** Build a rules engine over a structured scheme JSON, and use the LLM only to explain the results in plain language.

**Scheme landscape** (verify current figures before the demo; limits change):

| Scheme | Fits | Key parameters |
|---|---|---|
| **PMMY / Mudra** | Almost everyone | Shishu up to ₹50k, Kishore up to ₹5L, Tarun up to ₹10L, Tarun Plus up to ₹20L (for past Tarun repayers). No collateral, CGFMU-backed. |
| **PMEGP** (KVIC) | New units | Project up to ₹50L (manufacturing) / ₹20L (service). Subsidy 15–35% (higher for rural and special categories). Own contribution 5–10%. |
| **Stand-Up India** | SC/ST and women | ₹10L–₹1Cr, greenfield units |
| **PM Vishwakarma** | Traditional artisans (tailors, carpenters…) | ₹1L + ₹2L tranches at concessional 5% |
| **PMFME** | Micro food processing | 35% credit-linked subsidy, capped at ₹10L |
| **NABARD dairy / AHIDF / AIF** | Dairy, agri infrastructure | Interest subvention, sector-specific |
| **Maharashtra: CMEGP, Annasaheb Patil Mahamandal** | Local judges will recognise these | State subsidy, interest reimbursement. Check current terms. |
| **CGTMSE** | Collateral-free cover | An overlay on other loans |

**Nuances that impress judges:**
- **PMEGP subsidy is back-ended.** It is held as a term deposit for about 3 years, so the borrower pays EMI on the full loan at first. Most teams will simply subtract the subsidy and get the cash flow wrong.
- **Interest accrues during the moratorium.** The EMI after the moratorium is computed on principal plus accrued interest, or interest is serviced during it. Show both options.
- **Eligibility is multi-dimensional:** age, education (PMEGP requires 8th pass above certain project sizes), category (SC/ST/OBC/women/ex-servicemen), rural vs urban, new vs existing unit, previous subsidy taken.
- **Gap = cost − own capital − subsidy.** That figure is what drives the scheme you pick.

**Core math:** standard EMI formula, an amortisation table, break-even month from projected revenue, and DSCR (debt service coverage ratio, which is what banks actually check, ideally ≥1.25). DSCR is the one number that makes this look like a real loan tool.

## 6. Where GenAI earns its place (and where it shouldn't)

| Use GenAI for | Don't use GenAI for |
|---|---|
| Extracting structured intent from free text ("I want to start a 5-buffalo dairy in Junnar" → JSON) | EMI, subsidy and eligibility math |
| SWOT, risks, pricing narrative grounded in the computed numbers | Inventing competitor counts or population |
| Explaining schemes in simple Marathi or Hindi | Deciding eligibility |
| Cost breakdown templates (with a curated cost DB as the anchor) | Final interest rates |
| Answering follow-up questions over the generated report (RAG over scheme PDFs) | |

**Pattern:** tools/function calling. The LLM orchestrates calls such as `get_location_stats()`, `count_competitors()`, `match_schemes()` and `compute_emi()`, then narrates the results. That architecture slide alone signals you understood the brief.

## 7. Suggested architecture (hackathon-sized)

```
[Chat UI / Form]  ──►  LLM orchestrator (tool calling)
  (EN/HI/MR)              │
                          ├─ location_tool  → Census + LGD (pre-loaded SQLite/JSON)
                          ├─ competitor_tool → OSM Overpass
                          ├─ cost_tool      → curated cost templates per business
                          ├─ scheme_tool    → rules engine over schemes.json
                          └─ finance_tool   → EMI / amortisation / DSCR (pure functions)
                          ▼
              Report JSON ──► Dashboard (charts + what-if sliders)
                          └─► PDF export
```

**Stack:** Next.js or Streamlit, a single LLM API, SQLite or JSON for data, Recharts or Chart.js, and browser print-to-PDF or a PDF library. Skip vector DBs, microservices and auth. None of them win marks.

## 8. Risks and how to defuse them

| Risk | Mitigation |
|---|---|
| Hallucinated market numbers | Every number tagged with its source. LLM forbidden from inventing figures (system prompt plus structured output). |
| Stale scheme data | Date-stamp `schemes.json`; add a "verify at bank" disclaimer and links to official portals |
| Sparse rural OSM data | Fall back to district-level density × area. Label it "estimated". |
| "Advice" liability | Frame the output as an indicative assessment, not financial advice |
| Demo failure | Pre-cache two or three demo scenarios that run offline |

## 9. Winning demo narrative (3 minutes)

1. A persona: *"Sunita, 32, from a village in Pune district, has ₹60,000 and wants to start a tailoring unit."*
2. She types it in Marathi. The advisor asks two clarifying questions (category, education).
3. The dashboard shows households, number of tailors within 3 km, the gap, and a cost of ₹2.1L.
4. The engine matches schemes: PM Vishwakarma vs Mudra Kishore, side by side with EMI and DSCR.
5. What-if: drag capital to ₹1L and watch the loan, EMI and feasibility score change live.
6. Compare with a goatery idea in the same village. Tailoring wins on risk and goatery on margin.
7. Download a PDF in Marathi that she can take to the bank.

## 10. Questions to put to the organisers

- Is a specific state or region expected? (The Marathi requirement suggests Maharashtra.)
- Are you given datasets, or do you source your own?
- Is a specific LLM or provider mandated or banned?
- How is "hyper-local" evaluated? Do they expect real data or is mock data acceptable?
- Is voice input valued? It's a strong accessibility angle for rural users.

## Bottom line

The winning angle is a GenAI orchestrator over deterministic engines, built on real public data and clear about which numbers are estimates. Put your effort into the finance engine (PMEGP subsidy timing, moratorium interest, DSCR) and one fully loaded real district. Those two things will set you apart from the generic report generators.
