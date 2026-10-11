# Spec: V2 parallel build

Status: ready-for-agent

Parent spec: `.scratch/hyperlocal-dpr/spec.md`. Vocabulary: `CONTEXT.md`. Founding decision: ADR 0001. Split rules: `.scratch/v1-skeleton/v2-file-map.md` (owners, frozen files, known conflicts). Time box: **1 hour** (0:45–1:45). V3 keeps its own hour after it; the freed time is buffer.

## Grilling decisions (override anything below that conflicts)

- **Core scope only.** Protected: Bank View, Entrepreneur View with verifier, what-if, Verdict.
  - **AIML:** demo-path data only: Archetypes `dairy` + `kirana`; Schemes MUDRA, PMEGP, Stand-Up India; 3 Niphad villages (Lasalgaon + two more) hand-entered with real Census household counts, competitor counts as `assumption`. Then engine for those, verifier, LLM client + cache + `explain_report`, and Path to Yes last.
  - **Fullstack:** real auth (one small ticket), report persistence (create/get/list), stream replay from stored events, `run_pipeline` written. Fixture routes unchanged.
  - **Frontend:** (1) format + placeholder renderer + "Why this number?" sheet, (2) wizard posting a real intake with draft kept, (3) Explanation/Numbers/Bank DPR tabs with print and share, (4) what-if sheet, (5) language switch + account menu (may shrink to language only). 3 and 4 are protected.
- **Stretch (ticket range `40+`, unblocked, only if a persona finishes early):** chat (UI + tool loop), Compare (UI + summary), intake parse + describe box, BM25 retrieval, eval, the other 4 Archetypes and KCC/PM Vishwakarma/CMEGP, My Reports UI beyond the shell, voice/read-aloud. Their routes keep fixtures; the pitch doesn't claim them.
- **Tickets:** 3–5 per persona, ~10–20 min each, in persona folders `.scratch/v2-parallel/{aiml,fullstack,frontend}/`, numbered `01–09` AIML, `10–19` Fullstack, `20–29` Frontend, each with an `Owner:` line. How to work them: `plan.md` at the repo root. `Blocked by:` only names same-persona tickets; anything cross-persona is V3.
- **Scheme rules:** `verified_on` is set only after opening `source_url`; any figure that can't be confirmed is left out and listed in the ticket comment.
- **Translations:** Frontend writes `hi`/`mr` machine-assisted inside each screen ticket, flagged `needs native review`.
- **Figure id grammar** (from `api/contracts.py`): snake_case, `group.member` for group members (`cost.animals`), Comparison ids prefixed `<archetype_id>.` (`dairy.min_dscr`). Glossary: `CONTEXT.md` → Figure id.

## Problem Statement

The skeleton exists, but nothing in it is real. An Entrepreneur who opens the app at V1 exit:

- gets the same dairy DPR for Lasalgaon whatever they type. The wizard steps are one-line placeholders and Start posts a canned intake.
- reads `{{figure_id}}` placeholders instead of numbers in the Entrepreneur View, and can't tap a number to see where it came from.
- can't switch language, log in for real, save a report, try a what-if, compare businesses or ask a question.

Behind the screens, every engine, LLM and data loader function raises `NotImplementedError`. The Scheme and Archetype catalogues and the Niphad Locality data aren't written yet. Auth accepts any password, and no report is stored.

Three people now have three hours. They must work at the same time without breaking each other or the frozen contract. Then V3 can swap fixtures for the real engine and LLM in one hour.

## Solution

Each persona builds its own part against the frozen contract and the V1 fixtures, and proves it in isolation:

- **AIML** writes the hand-curated catalogues and Niphad Locality data. It implements the whole engine behind `run_engine`, the placeholder verifier, and the LLM layer: client with fallback, cache modes, Entrepreneur View and Comparison text, intake extraction, BM25 Scheme retrieval, chat tool loop and the 15-case eval. All of it runs without the API.
- **Fullstack** makes auth, users and report persistence real. Report create, stream, get and list work against the database. The stream still replays fixture stage events, but stores them per report so a reconnect replays them. Fullstack also writes the real pipeline driver, ready for V3 to switch on. Engine-backed and LLM-backed routes keep serving fixtures while `USE_FIXTURES=1`.
- **Frontend** turns every route from a shell into the real screen against the fixture API. That covers the wizard, placeholder filling, "Why this number?", the three report tabs with charts, Bank View print and share, what-if, chat, Compare, My Reports, the language switch and the account menu, all in English, Hindi and Marathi at 360 px.

At V2 exit, each persona's tickets pass their own checks. V3 is then plumbing: point the routes at `run_engine` and the LLM layer, drop `USE_FIXTURES`, record the demo cache.

## User Stories

### Entrepreneur: language and account (Frontend, Fullstack)
1. As an Entrepreneur, I want a language switch in the top bar that lists English, हिन्दी and मराठी in their own scripts, so that I can find mine without reading English.
2. As an Entrepreneur, I want my language choice remembered on this phone, so that I don't pick it again every visit.
3. As an Entrepreneur, I want every screen's copy in my chosen language, falling back to English only where a translation is missing, so that the app never shows a blank label.
4. As an Entrepreneur, I want amounts in Indian grouping (lakh) and with Devanagari digits in Hindi and Marathi, so that numbers look the way I say them.
5. As an Entrepreneur, I want to register with a username and password, so that I can come back to my reports.
6. As an Entrepreneur, I want to be told when a username is already taken, so that I pick another.
7. As an Entrepreneur, I want a clear message when my password is wrong, so that I know what to fix.
8. As an Entrepreneur, I want my password stored safely (hashed, never in plain text), so that a leaked database doesn't expose it.
9. As an Entrepreneur, I want to show and hide my password while typing, and have paste and my password manager work, so that logging in is easy.
10. As an Entrepreneur, I want to land back where I was after logging in, so that I don't lose my place.
11. As an Entrepreneur, I want an account menu with Log out and My Reports, so that a shared phone stays private.
12. As a guest Entrepreneur, I want to build, read, what-if, compare and chat without an account, so that nothing stops me trying it.

### Entrepreneur: intake wizard (Frontend)
13. As an Entrepreneur, I want a 4-step wizard (Where, Business, Money, About you) with a stepper showing where I am, so that the form feels short.
14. As an Entrepreneur, I want to go back to any earlier step, so that I can fix a mistake.
15. As an Entrepreneur, I want to pick district, block and village from lists, with search on the village list, so that I don't have to spell place names.
16. As an Entrepreneur, I want to see my village's household count once I pick it, so that I know the app knows my place.
17. As an Entrepreneur, I want to pick my business from large picture cards with an icon and a word, so that I can choose without reading much.
18. As an Entrepreneur, I want − and + buttons for business size, kept within the Archetype's allowed range, with a hint at the typical starting size, so that I choose something realistic.
19. As an Entrepreneur, I want a number keypad, quick amount chips and the amount written in words under the box ("₹1 lakh"), so that I don't add or miss a zero.
20. As an Entrepreneur, I want to answer only the eligibility questions my chosen Archetype needs, by tapping chips, so that the form stays short.
21. As an Entrepreneur, I want a one-line reason next to sensitive questions (category, schooling, past loans), so that I'm comfortable answering.
22. As an Entrepreneur, I want errors shown next to the question that needs fixing, so that I know exactly what's wrong.
23. As an Entrepreneur, I want my half-filled wizard kept if the page reloads, so that I don't start over on a bad connection.
24. As an Entrepreneur, I want to describe my idea in my own words above the wizard and have the form filled for me to check, so that I don't have to understand a form first.
25. As an Entrepreneur, I want to be told which fields the description didn't fill, so that I know what's left.
26. As an Entrepreneur, I want Start to build a DPR from what I actually entered, so that the report is about my business and not a sample.

### Entrepreneur: report (Frontend)
27. As an Entrepreneur, I want the Verdict card to show an icon, a plain word and a colour, plus the loan, EMI and Scheme, so that I get the answer first.
28. As an Entrepreneur, I want every `{{figure_id}}` in the advice replaced by the formatted number, so that I read numbers, not code.
29. As an Entrepreneur, I want each filled-in number to be tappable, so that I can ask "Why this number?".
30. As an Entrepreneur, I want the "Why this number?" sheet to show the formula, inputs, Source Badge and any note, so that I can trust or question it.
31. As an Entrepreneur, I want estimates labelled "Our estimate", so that I know which numbers to check.
32. As an Entrepreneur, I want a "numbers checked" badge showing verified / total, so that I know the AI didn't invent numbers.
33. As an Entrepreneur, I want the numbers still shown when the written advice is unavailable, so that I still get my answer.
34. As an Entrepreneur, I want Path to Yes changes listed when the Verdict isn't Feasible, each with a one-tap Try button, so that I have a way forward.
35. As an Entrepreneur, I want a Numbers tab with charts for means of finance, cost breakdown, profit over five years and outstanding loan, so that I see the money at a glance.
36. As an Entrepreneur, I want every chart to have a table view, so that I can read exact values.
37. As an Entrepreneur, I want a Source Badge on every key number, so that I know how solid it is.
38. As an Entrepreneur, I want a warning when few shops are mapped near my village, so that I don't over-trust the market estimate.
39. As an Entrepreneur, I want the best Scheme with its reasons, other eligible Schemes, and ineligible ones with unlock hints, each with terms, source link and verified-on date, so that I can talk to the bank.
40. As an Entrepreneur, I want a Bank DPR tab in English, bank format, with all standard sections, so that I can take it to a branch.
41. As an Entrepreneur, I want to download the Bank View as a PDF through the browser's print, on A4, so that I can print it.
42. As an Entrepreneur, I want one-tap WhatsApp sharing through the phone's share sheet, with copy-link as fallback, so that family or a bank officer can see the report.

### Entrepreneur: what-if, compare, chat, saved reports (Frontend)
43. As an Entrepreneur, I want sliders with − and + for Own Contribution, business size and tenure, so that I can explore options on a small screen.
44. As an Entrepreneur, I want what-if results to update as I change a value, so that I see the effect immediately.
45. As an Entrepreneur, I want to be told when a change switches the Scheme or the Verdict, so that I notice thresholds.
46. As an Entrepreneur, I want to reset my changes, and to turn them into a new DPR without losing the original, so that I can keep both.
47. As an Entrepreneur, I want to compare my business with one or two others for my own village and Own Contribution, so that I choose the best option.
48. As an Entrepreneur, I want metric rows with the better value marked by a check and the word "better", plus a summary paragraph, so that differences are clear.
49. As an Entrepreneur, I want to open a full DPR for any business in the Comparison, so that I can go deeper.
50. As an Entrepreneur, I want a chat sheet with suggested starter questions, so that I know what I can ask.
51. As an Entrepreneur, I want chat answers with filled-in numbers, Scheme citations that link to the source, and suggested changes I can apply, so that I can act on them.
52. As an Entrepreneur, I want chat never to change my saved report on its own, so that my DPR stays as I made it.
53. As a logged-in Entrepreneur, I want My Reports to list my saved reports with business, village, Verdict and date, so that I can reopen one.
54. As a new Entrepreneur, I want an empty state with a button to build my first DPR, so that I know what to do.
55. As an Entrepreneur, I want an offline banner and content-shaped loading placeholders, so that a slow phone still feels responsive.
56. As an Entrepreneur, I want a stage list with sources while my report builds, then the report opening by itself, so that I know the app is working.

### Fullstack: API behaviour
57. As the Frontend developer, I want register, login, logout and me to behave as the contract says (409 on a taken username, 401 on bad credentials, a session cookie on success), so that I can build the account flow against real behaviour.
58. As the Frontend developer, I want report create to store the intake and owner (or none for a guest) and return a new id, so that each report is its own record.
59. As the Frontend developer, I want get report to return the stored report for that id, and 404 for an unknown id, so that refresh and share links work.
60. As the Frontend developer, I want list reports to return only the current Entrepreneur's summaries, newest first, and 401 for guests, so that My Reports is private.
61. As the Frontend developer, I want the stream to store each stage event, mark the report done at the end, and replay stored events on reconnect, so that a dropped connection doesn't rebuild the report.
62. As the Frontend developer, I want simulate, compare, chat, intake parse and the catalogue routes to keep returning contract-shaped fixture data until V3, so that my screens have data now.
63. As the V3 integrator, I want a pipeline driver that runs intake, market, cost, schemes, DPR and explanation as stage events, stores the engine result and explanation, and finishes the report even when the LLM fails, so that switching off fixtures is one setting.
64. As the V3 integrator, I want every place that will call `run_engine` or the LLM layer marked in one spot per route, so that the swap is mechanical.

### AIML: data
65. As AIML, I want 6 Business Archetypes (dairy, onion cultivation, poultry, tailoring, kirana, flour mill) with unit-scale bounds, cost lines, operating assumptions, market mode and required eligibility fields, so that the engine has real inputs.
66. As AIML, I want 6 Schemes (MUDRA, PMEGP, Stand-Up India, PM Vishwakarma, CMEGP, KCC) as declarative eligibility rules and terms, each rule with `source_url` and `verified_on`, so that every Scheme figure can be traced.
67. As AIML, I want the official scheme text saved for citations, so that BM25 retrieval has something to search.
68. As AIML, I want Niphad villages with LGD codes, Census household counts and per-Archetype map competitor counts, and a seed step that loads them into the database, so that Locality analysis runs on real places.
69. As AIML, I want loaders that validate every catalogue file against its model and fail loudly on a bad file, so that a typo never reaches the engine.

### AIML: engine
70. As AIML, I want `run_engine` to return a full `EngineResult` for every Archetype and the 3 eval villages, so that the API can switch to it in V3.
71. As AIML, I want every number the engine produces registered as a Figure with value, unit, Source Badge and, where computed, formula and inputs, so that "Why this number?" and the placeholder registry work.
72. As AIML, I want EMI, moratorium (capitalised vs serviced), PMEGP back-ended subsidy, MUDRA tiers, KCC bullet repayment and interest subvention computed in integer rupees, so that the Bank View matches a bank calculator.
73. As AIML, I want Market Gap only for local Archetypes and skipped for Aggregators, so that dairy and onion aren't judged on village demand.
74. As AIML, I want the Verdict to be the worst of its four signals, so that one bad signal can't be hidden.
75. As AIML, I want Path to Yes to suggest the smallest change that really reaches Feasible when re-run, so that the advice is honest.

### AIML: LLM layer
76. As AIML, I want one client that calls Gemini first and Groq on failure, with live, record and replay modes keyed on model, messages and tools, so that the demo runs without internet.
77. As AIML, I want the Entrepreneur View and the Comparison summary generated in the chosen language with placeholders only, so that no digit ever comes from the LLM.
78. As AIML, I want `verify` to reject ASCII digits, Devanagari digits and unknown placeholder ids, and to accept namespaced Comparison ids, so that rule 4 is enforced in code.
79. As AIML, I want explanation to regenerate once on a failed verify, then strip the offending sentences and report verified / total, so that a bad generation degrades instead of failing.
80. As AIML, I want free-text intake extraction that returns a partial intake, with the missing fields computed in code, so that "describe in your own words" fills the form.
81. As AIML, I want a chat loop with read-DPR, search-schemes and simulate tools that returns citations and suggested changes but never mutates the report, so that the advisor stays read-only.
82. As AIML, I want an eval script over 15 cases (5 Archetypes × 3 Niphad villages) reporting scheme-match accuracy and verifier pass rate, so that the pitch quotes measured numbers.

## Implementation Decisions

### Split and ownership
- Work is split strictly by the V2 file map. A ticket edits only its owner's paths. Frozen files stay untouched: contract, generated types, dependency manifests and lockfiles, API app entry, web router, i18n loader, fixtures.
- **The contract doesn't change in V2.** Fill a gap inside the existing models. If a real contract change is unavoidable, it is a Fullstack ticket that all three personas agree on, and it regenerates the TypeScript types in the same commit.
- New endpoints go into one of the eight existing router modules. New screens go inside an existing route as a tab, sheet or step. New copy goes into a new or existing i18n namespace file, with Hindi and Marathi falling back to English.

### AIML
- **Engine:** implement the declared functions behind `run_engine` (market, cost, schemes, finance, verdict, path to yes, figure registry). Keep the existing signatures. The engine stays pure: catalogues, the village and `current_year` come in as arguments, and it never reads the clock or a file.
- **Figure ids** follow the grammar in Grilling decisions (for example `funding_gap`, `cost.animals`, `min_dscr`). The registry rejects a duplicate id. These ids are the placeholder vocabulary that prompts and the frontend use, so the fixture report's ids are the starting set. Add to them, don't rename them.
- **Scheme rules** are data: field, operator, value, optional conditions and an Entrepreneur-facing message, evaluated over intake fields and derived values (Own Contribution %, project cost). One small rule evaluator covers all six Schemes. A Scheme gets no special-case code, except for its repayment shape: back-ended subsidy (PMEGP), tiers (MUDRA), bullet repayment and subvention (KCC).
- **Money is integer rupees, rates are percent, durations are months**, end to end. Rounding happens once, where a rupee amount is produced.
- **Catalogue files** live under the data folder, one JSON per Archetype and one per Scheme. Loaders return validated models from the data package, and the API reads catalogues only through them. Never invent a Scheme figure: if a value can't be sourced, leave the rule out and note it in the ticket.
- **LLM layer:** an OpenAI-compatible client. Gemini is primary and Groq is the fallback, both configured from env. The cache key is a hash of model, messages and tools. Replay mode raises on a cache miss instead of calling out. Prompts live as markdown files beside the code. Entrepreneur View and Comparison prompts get the Figure ids and units but not the values. The verifier's result type, verified / total plus stripped sentences, feeds `Explanation`.
- **Retrieval** is BM25 over the saved scheme text, returning `Citation`s with the Scheme's source URL. No embeddings.
- **Chat** is a tool-calling loop. Simulate goes through `run_engine` with a changed intake and returns its Figures as extra figures. The reply uses placeholders from the report's Figures plus those extra figures. Suggested changes go back as data, never applied.
- Every AIML function the API will call takes and returns contract models (known conflict 5), so V3 wiring is one call per route.

### Fullstack
- **Auth:** a user table, usernames unique. Passwords use standard-library scrypt in the declared `scrypt$<salt>$<hash>` format and are compared in constant time. The signed session cookie holds the user id. Register returns 409 on a duplicate username, and login returns 401 on a bad username or password, with the same message for both.
- **Reports:** create stores the report as pending with its intake, the owner (null for a guest) and a new UUID. Get reads it back and returns 404 for an unknown id. List returns the owner's summaries newest first and 401 for a guest.
- **Stream:** while `USE_FIXTURES=1`, the stream replays the fixture stage events but stores them on the report row and saves the fixture engine result and explanation against the report's own id. Any later open replays the stored events instead of re-running.
- **Pipeline driver:** implement `run_pipeline` to the order and failure rules in the parent spec (stages, stored events, LLM failure still completes with the explanation marked unavailable). It's only called when fixtures are off, so it's exercised in V3. V2 leaves it written and type-checked.
- Engine-backed and LLM-backed routes (simulate, compare, chat, intake parse) and the catalogue routes keep their fixture bodies. Each fixture use carries a `shortcut:` comment naming the V3 call that replaces it.

### Frontend
- **Formatting:** implement the two declared format functions with the browser's native number formatting: Indian grouping, Devanagari digits for `hi` and `mr`, and the Bank View always in English. The API never formats.
- **Placeholders:** one shared renderer turns text with `{{figure_id}}` (and namespaced Comparison ids) into text plus Figure chips, using the report's Figures (plus chat's extra figures). An unknown id renders as a dash and never as raw braces.
- **Wizard:** the four step components and the describe box collect a real `IntakeInput`. The draft lives in local storage under one key and is cleared on a successful create. The canned intake file is deleted. Archetype bounds and required eligibility fields come from the catalogue route.
- **Report:** build Explanation, Numbers and Bank DPR tabs, the Verdict card, the "Why this number?" sheet, the what-if sheet (through the simulate hook) and the chat sheet (through the chat hook) from the existing components. Charts use Recharts and each one has a table toggle. Print uses an A4 print stylesheet that shows only the Bank View.
- **Shell:** the app bar gets the language switch and account menu. My Reports, Login and Compare use their hooks. Compare takes the village and Own Contribution from the Entrepreneur's current report or wizard draft, not from the fixture.
- **UI rules:** 360 px first, 48 px targets, one amber primary button per screen, an icon and a word on every option, light theme, Mukta font. Jargon appears only in the Bank DPR tab.

## Testing Decisions

- **What makes a good test:** it drives one public seam and checks what comes out (numbers, shapes, status codes, stage order). It never tests private helpers. Expected values are worked out by hand (an EMI from a bank calculator, a subsidy from the Scheme's official terms), never copied from the code's own output.
- **Seam 1, `run_engine`** (AIML, `tests/engine/`). It covers every calculation case listed in the parent spec's Testing Decisions: EMI, moratorium, PMEGP lock-in, MUDRA tier boundaries, unlock hint, KCC bullet repayment, market mode, worst-signal Verdict, Path to Yes reaching Feasible, and the schedule closing at zero. Build the inputs in the test from loaded catalogues and a village dict. Every engine function keeps at least one `assert` check (CLAUDE.md rule 2).
- **Seam 2, `verify(text, figures)`** (AIML, the verifier test file): valid placeholders pass; ASCII digits, Devanagari digits and unknown ids fail; namespaced Comparison ids resolve.
- **Catalogue validation** sits under seam 1, not as a separate seam. A data test loads every catalogue through the loaders and asserts that every Scheme rule has a `source_url` and a `verified_on`.
- **LLM layer:** tested in replay mode only. A test that needs an LLM reply records it once and commits the cache file, and CI never calls out. The eval script is run by hand, and its numbers go in the ticket comment.
- **Seam 3, the HTTP API** (Fullstack, the API smoke test file). Each run uses an in-process test client and a fresh SQLite database with `USE_FIXTURES=1`. Cases:
  - register, then a duplicate register gets 409
  - a wrong password gets 401
  - login, me and logout
  - a guest gets 401 on list
  - create, then stream: stage order and the done event
  - get returns the stored report under its own id
  - a second stream replays the stored events
  - list shows only the owner's reports, newest first
  - unknown id gets 404

  Build test data inside the test file and never edit fixtures (known conflict 7).
- **Frontend:** no automated tests (parent spec). The check is `npm run check` and `npm run build` passing, plus the scripted demo path in `docs/wireframes.md` run against the fixture API at a 360 px frame in English and Marathi with no console errors.
- **Prior art:** the V1 declaration tests (`tests/engine/`, `tests/llm/`, `tests/data/`) show the import-and-signature pattern. `tests/test_api_smoke.py` shows the test client and contract validation. `tests/test_fixtures.py` shows model validation of JSON. V2 replaces each declaration test with behaviour tests as its functions become real.

## Out of Scope

- Switching routes from fixtures to the real engine and LLM, removing `USE_FIXTURES`, recording the demo LLM cache, the Neon switch check and the two full demo runs. All of these are V3.
- Any change to the API contract, the generated types, dependencies, the router or the i18n loader.
- Voice transcription and read-aloud, beyond keeping the V1 stub working (stretch, first on the cut list).
- Localities beyond Niphad, and more than 6 Archetypes or 6 Schemes.
- Native-speaker review of Hindi and Marathi strings (before the event, not in V2).
- Frontend automated tests, dark theme, offline-first sync.

## Further Notes

- **Order inside V2:** AIML starts with data, because the engine tests need catalogues, then the engine, then the verifier, then the LLM layer. Fullstack starts with auth, then report persistence and stream replay, then the pipeline driver. Frontend starts with format and placeholders, because every report screen needs them, then the wizard, then the report tabs, then the sheets, Compare and My Reports.
- **Cut order if behind** (from the parent spec): voice, chat tools beyond reading the DPR, Comparison, translated homepage copy, read-aloud. Protected: Bank View, Entrepreneur View with the verifier, what-if, Verdict.
- **Figure ids are the one cross-persona agreement V2 relies on** outside the contract: AIML's engine produces them, prompts reference them, Frontend renders them. The fixture report is their source of truth until V3. AIML notes any added id in its ticket comment.
- **V2 exit:** each persona's tickets are done and their checks pass. `uv run pytest` is green, and `npm run check` and `npm run build` pass. The file map check still passes.
