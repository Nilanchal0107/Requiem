# Spec: Hyper Local Business & Loan Advisory (DPR builder)

Status: ready-for-agent

Vocabulary: `CONTEXT.md`. Founding decision: ADR 0001 (code computes every number and the Verdict; the LLM only explains). Supporting docs: `docs/prd.md`, `docs/trd.md`, `docs/architecture.md`, `docs/api-contracts.md`, `docs/ui-ux.md`, `docs/wireframes.md`.

## Problem Statement

A first-time rural Entrepreneur in a village like Lasalgaon (Niphad block, Nashik) has a business idea, such as a five-buffalo dairy, but no reliable way to answer three questions:

- Will this work in my Locality?
- How much money do I need, and how much must I borrow?
- Which government Scheme can I get, and what will I repay each month?

Generic advice ignores their village, their savings and their eligibility. Banks ask for a Detailed Project Report (DPR) that people pay consultants to write and then can't read. Most AI tools invent numbers that change every time and can't be defended at the bank counter.

The Entrepreneur is usually on a budget Android phone, often outdoors, on patchy mobile data, and more comfortable in Marathi or Hindi than English.

## Solution

A mobile-first web app.

1. The Entrepreneur picks their Locality, a Business Archetype, a unit scale, their Own Contribution and a few eligibility details. They can tap through a 4-step wizard or describe the idea in their own words and let the app fill the form.
2. The app builds a DPR with deterministic code:
   - Locality market analysis from Census and map data
   - Project Cost
   - Funding Gap
   - the best matching Scheme, with reasons and unlock hints for the ones that don't fit
   - loan terms and the repayment schedule
   - 5-year projections, DSCR and break-even
   - a Verdict, plus a Path to Yes when the Verdict isn't Feasible
3. The DPR has two views:
   - a **Bank View** in bank format (English, printable to PDF, shareable on WhatsApp)
   - an **Entrepreneur View** that explains the same numbers in plain Marathi, Hindi or English, where every number is a Verified Figure the Entrepreneur can tap to see its formula and source
4. The Entrepreneur can:
   - try changes live (what-if)
   - compare two or three Business Archetypes
   - ask questions in chat
   - save reports with an account, or use everything as a guest

## User Stories

### Discovering the app
1. As an Entrepreneur, I want a homepage that says in one sentence what the app does, so that I know whether it's for me.
2. As an Entrepreneur, I want to see the three questions the app answers, so that I recognise my own problem.
3. As an Entrepreneur, I want to see which government Schemes are covered, so that I trust it knows real loans.
4. As an Entrepreneur, I want to see why I can trust the numbers, so that I'm not misled by a guess.
5. As an Entrepreneur, I want a single clear "Start my DPR" button, so that I know what to tap next.
6. As a judge, I want the homepage to explain the problem, the uniqueness and the features, so that I understand the product before the demo.

### Language
7. As an Entrepreneur, I want to switch the app between English, Hindi and Marathi at any time, so that I can read it comfortably.
8. As an Entrepreneur, I want each language listed in its own script, so that I can find mine without reading English.
9. As an Entrepreneur, I want my language choice remembered, so that I don't pick it again every visit.
10. As an Entrepreneur, I want amounts shown in lakh and with Devanagari digits in Hindi or Marathi, so that numbers look the way I say them.
11. As an Entrepreneur, I want bank jargon replaced by plain phrases ("Can your profit pay the EMI?"), so that I understand what each number means.

### Account
12. As an Entrepreneur, I want to use the app without creating an account, so that nothing stops me from trying it.
13. As an Entrepreneur, I want to create an account with a username and password, so that I can come back to my reports.
14. As an Entrepreneur, I want my password manager and paste to work on the login form, so that logging in is easy.
15. As an Entrepreneur, I want to see and hide my password while typing, so that I don't make mistakes.
16. As an Entrepreneur, I want a clear message when my login is wrong, so that I know what to fix.
17. As an Entrepreneur, I want to return to where I was after logging in, so that I don't lose my place.
18. As an Entrepreneur, I want to log out from the account menu, so that a shared phone stays private.

### Intake
19. As an Entrepreneur, I want to describe my idea in my own words (in Marathi, Hindi or English), so that I don't have to understand a form first.
20. As an Entrepreneur, I want the app to fill the form from my description and ask me to check it, so that I stay in control of my details.
21. As an Entrepreneur, I want to pick my district, block and village from lists, so that I don't have to spell place names.
22. As an Entrepreneur, I want to search the village list, so that I find my village quickly among many.
23. As an Entrepreneur, I want to see my village's household count once I pick it, so that I know the app knows my place.
24. As an Entrepreneur, I want to choose my business from large picture cards, so that I can choose without reading much.
25. As an Entrepreneur, I want to set the size of my business with − and + buttons (animals, acres, machines), so that I don't need to type.
26. As an Entrepreneur, I want a hint about a typical starting size, so that I choose something realistic.
27. As an Entrepreneur, I want to enter my own money with a number keypad and quick amount chips, so that entry is fast.
28. As an Entrepreneur, I want to see the amount I typed written in words ("₹1 lakh"), so that I don't add or miss a zero.
29. As an Entrepreneur, I want to answer only the eligibility questions that matter for my business, so that the form stays short.
30. As an Entrepreneur, I want to answer eligibility questions by tapping chips, so that I don't need dropdowns or typing.
31. As an Entrepreneur, I want to know why the app asks about my category, schooling and past loans, so that I'm comfortable answering.
32. As an Entrepreneur, I want to see which step I'm on and go back to any earlier step, so that I can fix mistakes.
33. As an Entrepreneur, I want errors shown next to the question that needs fixing, so that I know exactly what's wrong.
34. As an Entrepreneur, I want my half-filled form kept if the page reloads, so that I don't start over on a bad connection.

### Building the DPR
35. As an Entrepreneur, I want to see each stage of the report being built (my village, cost, schemes, DPR, advice), so that I know the app is working and what it's checking.
36. As an Entrepreneur, I want each stage to show where its data came from, so that I trust the result.
37. As an Entrepreneur, I want to see when the app re-checks its own advice, so that I trust it catches its mistakes.
38. As an Entrepreneur, I want the report to open automatically when it's ready, so that I don't have to tap again.
39. As an Entrepreneur, I want a clear message and a retry button if something fails, so that I'm not stuck.
40. As a judge, I want to see the pipeline stages, timings and sources live, so that I can see the system's reasoning, not just a chat bubble.

### Verdict and the Entrepreneur View
41. As an Entrepreneur, I want a plain Verdict at the top ("Good to start", "Possible with changes", "Not advisable right now"), so that I get the answer first.
42. As an Entrepreneur, I want the Verdict shown with an icon and a word as well as colour, so that I understand it even if I can't tell colours apart.
43. As an Entrepreneur, I want one line explaining the main reason for the Verdict, so that I know what drives it.
44. As an Entrepreneur, I want the loan amount, monthly EMI and Scheme name next to the Verdict, so that I see the key commitment at once.
45. As an Entrepreneur, I want a simple explanation of whether my business can work in my village, so that I understand the market.
46. As an Entrepreneur, I want my money plan explained (total needed, my share, what I borrow, when EMI starts), so that I know my commitment.
47. As an Entrepreneur, I want strengths and risks listed simply, so that I know what to watch out for.
48. As an Entrepreneur, I want pricing tips for my business, so that I can earn enough to repay.
49. As an Entrepreneur, I want numbered next steps with a document checklist, so that I know what to do at the bank.
50. As an Entrepreneur, I want to tap any number and see "Why this number?" with its formula, inputs and source, so that I can trust or question it.
51. As an Entrepreneur, I want estimates clearly marked as "Our estimate" with a way to change them, so that I can correct what I know better.
52. As an Entrepreneur, I want a badge saying all numbers in the advice were checked, so that I know the AI didn't invent them.
53. As an Entrepreneur, I want to hear the explanation read aloud, so that I can understand it without reading (stretch).
54. As an Entrepreneur, I want the numbers still shown if the written advice can't be produced, so that I still get my answer.

### Path to Yes
55. As an Entrepreneur whose Verdict isn't Feasible, I want to see the smallest changes that would make it work (more Own Contribution, a smaller start, a longer tenure), so that I have a way forward instead of a dead end.
56. As an Entrepreneur, I want to try a suggested change with one tap, so that I can see its effect immediately.

### Schemes
57. As an Entrepreneur, I want to see the best Scheme for me with the reasons I qualify, so that I know why it was chosen.
58. As an Entrepreneur, I want to see the other Schemes I qualify for, so that I can discuss options with the bank.
59. As an Entrepreneur, I want to see why I don't qualify for a Scheme and what would change that, so that I know what to work towards.
60. As an Entrepreneur, I want each Scheme to show its interest rate, maximum loan, tenure and months before EMI starts, so that I understand the terms.
61. As an Entrepreneur, I want each Scheme to link to its official source and show when it was last checked, so that I can verify it.
62. As an Entrepreneur starting a PMEGP-funded unit, I want to see that the subsidy arrives later and doesn't reduce my early EMIs, so that I'm not surprised by the cash flow.
63. As an onion farmer, I want my loan to be matched to KCC with repayment at harvest, so that the plan fits how farming income arrives.
64. As a woman or SC/ST Entrepreneur, I want Schemes meant for me (such as Stand-Up India or higher PMEGP subsidy) to be considered automatically, so that I don't miss benefits.

### Numbers and charts
65. As an Entrepreneur, I want a chart of where the money comes from (my share, loan, subsidy), so that I see the split at a glance.
66. As an Entrepreneur, I want a chart of what the money is spent on, so that I know the biggest costs.
67. As an Entrepreneur, I want a chart of profit over five years, so that I see how the business grows.
68. As an Entrepreneur, I want to see the outstanding loan over time, so that I know when I'll be debt-free.
69. As an Entrepreneur, I want every chart available as a simple table, so that I can read exact values.
70. As an Entrepreneur, I want each key number to show its source badge (Census, Map, You entered, Our estimate, Govt scheme, Calculated), so that I know how solid it is.
71. As an Entrepreneur, I want a warning when few shops are mapped near my village, and a way to enter how many competitors I know of, so that the market estimate isn't wrong.

### Bank View
72. As an Entrepreneur, I want a bank-format DPR in English with all standard sections, so that I can take it to a bank branch.
73. As an Entrepreneur, I want to download the DPR as a PDF, so that I can print it.
74. As an Entrepreneur, I want to share my report link on WhatsApp in one tap, so that family or a bank officer can see it.
75. As a bank officer, I want the DPR to show the project cost breakdown, means of finance, repayment schedule, projections, break-even and DSCR, so that I can assess the loan quickly.
76. As a bank officer, I want the sources and verification dates listed, so that I know how current the figures are.

### What-if
77. As an Entrepreneur, I want to change my own money, business size and repayment period and see the result immediately, so that I can explore options.
78. As an Entrepreneur, I want − and + buttons next to every slider, so that I can make precise changes on a small screen.
79. As an Entrepreneur, I want to be told when a change switches the Scheme or the Verdict, so that I notice important thresholds.
80. As an Entrepreneur, I want to reset my changes, so that I can start again.
81. As an Entrepreneur, I want to turn my changes into a new DPR without losing the original, so that I can compare and keep both.
82. As an Entrepreneur, I want what-if results to appear even without internet, so that slow data doesn't stop me exploring.

### Comparison
83. As an Entrepreneur, I want to compare my business with one or two others in the same village with the same money, so that I choose the best option.
84. As an Entrepreneur, I want the comparison to show Verdict, loan, EMI, profit check, payback, Scheme and market side by side, so that differences are clear.
85. As an Entrepreneur, I want the better value in each row marked with a check and a word, so that I don't have to work it out.
86. As an Entrepreneur, I want a short paragraph on which business suits me, so that I get a recommendation in words.
87. As an Entrepreneur, I want to open a full DPR for any business in the comparison, so that I can go deeper.

### Chat advisor
88. As an Entrepreneur, I want to ask questions about my DPR in my own language, so that I can clear doubts.
89. As an Entrepreneur, I want suggested questions to start with, so that I know what I can ask.
90. As an Entrepreneur, I want answers about Schemes to cite the official source, so that I can trust them.
91. As an Entrepreneur, I want the advisor to try a change for me ("what if I start with 3 animals?") and offer it as a suggestion, so that I can apply it if I like.
92. As an Entrepreneur, I want the advisor never to change my saved report on its own, so that my DPR stays as I made it.
93. As an Entrepreneur, I want to speak my question instead of typing it, so that chat is easier (stretch).

### My Reports
94. As a logged-in Entrepreneur, I want a list of my saved reports with business, village, Verdict and date, so that I can reopen one.
95. As a logged-in Entrepreneur, I want a saved report to open instantly with the same numbers, so that it matches what I took to the bank.
96. As a new user, I want a helpful empty state with a button to build my first DPR, so that I know what to do.

### Reliability and access
97. As an Entrepreneur, I want a clear banner when I'm offline, so that I understand why something doesn't load.
98. As an Entrepreneur, I want placeholders shaped like the content while it loads, so that the app feels responsive on a slow phone.
99. As an Entrepreneur, I want every button big enough to tap easily, so that I don't hit the wrong one.
100. As an Entrepreneur with a screen reader, I want labels, focus order and announcements to work, so that I can use the app.
101. As an Entrepreneur who prefers less motion, I want animations turned off when my phone asks for it, so that the app is comfortable.
102. As a presenter, I want the full demo to run without internet using recorded AI responses, so that venue wifi can't break it.
103. As a presenter, I want a measured scheme-match accuracy and verification rate from a 15-case test set, so that I can quote honest numbers in the pitch.

## Implementation Decisions

### Modules
- **Engine:** a pure calculation module with one public entry point, `run_engine(input, archetype, schemes, village) → EngineResult`. It computes:
  - Locality market
  - Project Cost (including working capital)
  - Funding Gap
  - Scheme matching with reasons and unlock hints
  - loan terms and the repayment schedule
  - 5-year projections, DSCR, break-even and payback
  - the Verdict and Path to Yes

  It does no network, database, LLM or file I/O. Catalogue and Locality data are passed in as arguments. Path to Yes calls the engine again with Path to Yes disabled.
- **LLM layer:**
  - one OpenAI-compatible client pointed at Gemini (primary) with Groq fallback
  - a cache with three modes: live, record, replay
  - Entrepreneur View and Comparison summary generation
  - a placeholder verifier
  - free-text intake extraction
  - BM25 retrieval over official scheme text
  - a tool-calling chat loop (tools: read DPR, search schemes, simulate)
  - an eval script
- **Data:**
  - hand-curated Business Archetype and Scheme catalogues, each Scheme with a source link and verified-on date
  - official scheme text for citations
  - Niphad Census and map source files
  - a catalogue loader
  - a seed step that loads Locality data into the database
- **API:** HTTP routes, session auth, the report pipeline driver that streams stage events, persistence, and the single definition of every request and response model.
- **Web:** a mobile-first single-page app with routes for Home, Login, New (wizard plus stage trace), Report (Explanation / Numbers / Bank DPR tabs, what-if, chat), Compare and My Reports.

### Architectural decisions
- Code computes every number, Scheme match and Verdict; the LLM only explains (ADR 0001).
- **LLM text never contains digits.** The LLM writes `{{figure_id}}` placeholders that the frontend fills from the engine's figure registry. The verifier rejects unknown ids and any ASCII or Devanagari digit outside a placeholder. It regenerates once (emitting a visible "retrying" stage), then strips offending sentences and reports verified / total.
- **Every engine number is a Figure** carrying value, unit, Source Badge (census, osm, user, assumption, scheme, computed), and optional formula, inputs and note. All Figures are indexed by id in the engine result; that index is the placeholder registry.
- **Market modes:** local Archetypes compare household demand against competitor capacity to get a Market Gap. Aggregator Archetypes (dairy to a cooperative, onion to the Lasalgaon APMC) aren't limited by local demand and skip the Market Gap signal.
- **Scheme eligibility** is data, not code: declarative rules (field, operator, value, optional conditions, message) evaluated over intake fields and derived values. MUDRA uses tiers. PMEGP's capital subsidy is back-ended: it reduces the outstanding principal at the end of the lock-in period, not the early EMIs. KCC uses bullet repayment and interest subvention.
- **Verdict** is the worst of four signals: minimum DSCR (≥1.5 / ≥1.25 / below), Market Gap (local mode only), payback vs tenure, and whether any Scheme is eligible.
- **Money** is integer rupees end to end. Rates are percent and durations are months. The API never formats numbers; the frontend formats per language with the browser's native number formatting.
- **Report lifecycle:**
  1. Creating a report stores it as pending and returns its id.
  2. Opening its stream runs the pipeline (intake, market, cost, schemes, DPR, explanation) and streams stage events.
  3. Stage events are stored so a reconnect replays them.
  4. An LLM failure still completes the report, with the explanation marked unavailable.
- **Persistence:** a relational store via an ORM, SQLite by default and switchable to hosted Postgres through one connection setting. It holds users, reports (input, engine result and explanation as JSON, stage events, owner or none for guests) and villages (LGD codes, Census counts, map competitor counts per Archetype). Catalogues stay in version-controlled JSON.
- **Auth:** a signed session cookie, passwords hashed with the standard-library scrypt. Guests can do everything except list saved reports.
- **Contract:** request/response models are defined once in the API. The frontend's types are generated from the API's OpenAPI schema and never hand-edited. The contract is frozen after V1.
- **Ownership:**
  - Frontend owns the web app
  - Fullstack owns the API, the generated types, fixtures and root config
  - AIML owns engine, LLM layer, data and their tests

  Nobody edits outside their own area.

### API contract (summary; full shapes in `docs/api-contracts.md`)
- **Auth:** register, login, logout, me.
- **Catalogue:**
  - localities (districts → blocks → villages, chosen by query)
  - archetypes, including unit-scale bounds and required eligibility fields
  - schemes, with terms, source and verified-on date
- **Intake parse:** free text and language → partial intake plus a list of missing fields (computed in code).
- **Reports:**
  - create → id
  - stream → stage events then done or error
  - get one → full report
  - list → current user's summaries; guests get 401
- **Simulate:** intake → engine result. No LLM, nothing saved, target under 100 ms.
- **Compare:** intake plus 2–3 archetype ids → engine results plus a summary paragraph. Its placeholders are namespaced by archetype.
- **Chat:** report id, message, history and language → reply with placeholders, extra figures from simulate, citations, suggested changes and tools used.
- **Voice transcribe** (stretch): audio → text.

### UX decisions (full spec in `docs/ui-ux.md` and `docs/wireframes.md`)
- **Design target:** mobile-first at 360 px, light theme only, deep green brand with amber reserved for the one primary action per screen, Mukta font self-hosted for Latin and Devanagari, Lucide icons, 48 px touch targets.
- **Navigation:** a top app bar only (language switch, account menu), plus one sticky bottom action bar per screen.
- **Intake:** a 4-step wizard (Where, Business, Money, About you) with an optional "describe in your own words" shortcut above it. The draft is kept in local storage.
- **Report page:** a Verdict card above sticky tabs (Explanation as the default, Numbers, Bank DPR). The bottom bar holds Try changes and Ask. Figures open a "Why this number?" bottom sheet. What-if and chat are bottom sheets on mobile and side panels on desktop.
- **Comparison:** metric rows instead of tables. The better value gets a check icon and the word "better".
- **Sharing and PDF:** sharing uses the native share sheet with copy-link fallback. PDF is browser print with an A4 print stylesheet.
- **Copy:** jargon is used only in the Bank DPR tab; Verdict labels are written in plain words in all three languages.

## Testing Decisions

- **What makes a good test here:** it exercises external behaviour through a public seam and asserts on observable outputs (numbers, shapes, status codes, stage order), never on internal helpers or private structure. Expected values are hand-checked (e.g. an EMI matched against a bank calculator), not copied from the code's own output.
- **Seam 1, the engine entry point** (`run_engine`). Covers all calculation behaviour. Required cases:
  - EMI against a hand-checked value
  - capitalised vs serviced moratorium
  - PMEGP back-ended subsidy changing the outstanding balance exactly at the end of lock-in and not before
  - MUDRA tier selection at each boundary
  - an Own Contribution percentage failure producing an unlock hint
  - KCC bullet repayment
  - aggregator vs local market mode
  - the Verdict taking the worst signal
  - a Path to Yes change that really reaches Feasible when re-run
  - a repayment schedule closing at exactly zero
- **Seam 2, the HTTP API** (in-process test client, LLM in replay mode, fresh SQLite per run):
  - one contract-validating smoke test per endpoint
  - register / login / me / logout and the guest-gets-401 rule
  - report create → stream (stage order, done event) → get
  - simulate never touching the LLM or the database
  - compare returning one result per archetype
  - chat returning citations and suggested changes
  - one end-to-end test of the demo persona (dairy, Niphad, ₹1 lakh, woman, OBC, 10th pass, Marathi) asserting a complete report with every Entrepreneur View placeholder resolving
- **Seam 3, the verifier** (`verify(text, figures)`): accepts valid placeholders; rejects ASCII digits, Devanagari digits and unknown ids; Comparison namespaced ids resolve.
- **Eval:** a 15-case set (5 Archetypes × 3 Niphad villages) with hand-labelled expected Schemes, run through seam 1, reporting scheme-match accuracy and verifier pass rate for the pitch.
- **No frontend tests.** The scripted demo path in `docs/wireframes.md`, run twice end to end at a 360 px device frame during V3, is the UI acceptance test.
- **Prior art:** none yet; the repository has no code. These suites set the pattern for future tests.

## Out of Scope

- Localities beyond Niphad block, Nashik; more than the 6 Business Archetypes and 6 Schemes.
- Live scheme scraping or any scheme API (none provides usable eligibility rules); live map queries at runtime.
- Real loan applications, bank integrations, KYC, payments, OTP/SMS, OAuth or Supabase Auth.
- A public deployment (localhost demo only; hosted Postgres is wired for the switch only).
- Dark theme, a native app, offline-first sync, push notifications.
- Embeddings, vector databases, rerankers, graph RAG, fine-tuning, multi-agent frameworks, low-code tools.
- Tax computation in projections (micro-enterprise assumption, labelled).
- Frontend automated tests.
- Detecting numbers written as words in LLM text (forbidden by prompt; residual risk accepted).

## Further Notes

- **Delivery is versioned** (5 hours of build, 1 hour for the pitch):
  - **V1 (skeleton):** the contract is frozen, every endpoint returns fixture data, and every route renders. AIML builds data and engine in parallel; Frontend builds homepage and design system.
  - **V2:** parallel work against the contract.
  - **V3:** merge, real engine and LLM, record the demo cache, two full demo runs.
  - Tickets go in `.scratch/v1-skeleton/`, `.scratch/v2-parallel/` and `.scratch/v3-merge/`, each naming its owner persona and the tickets it's blocked by.
- **Cut order if behind:** voice, chat tools beyond reading the DPR, Comparison, translated homepage copy, read-aloud. The Bank View, Entrepreneur View with verifier, what-if and Verdict are protected.
- **Before the event:**
  - Re-verify every Scheme figure against its official source (PMEGP FY26-27 status, MUDRA Tarun Plus, KCC subvention limit after Budget 2025, CMEGP terms, PM Vishwakarma tranches).
  - Have a native speaker review Hindi and Marathi strings.
  - Prepare Niphad Census and map data.
  - Ask organisers whether preparing public data in advance is allowed (all code is written during the event).
