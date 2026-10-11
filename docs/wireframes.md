# Wireframes

Mobile-first ASCII wireframes at **360 px wide**. Each frame is one screen or state. Tokens, components and behaviour are in [`ui-ux.md`](ui-ux.md); component names in `[Brackets]` match its §4. Copy is in English here. Real strings live in `web/src/i18n/*.json` (EN/HI/MR).

**Legend**
```
[■ Button]      amber primary (one per screen)
[□ Button]      secondary
‹ Back          back chevron in AppBar
( chip )        unselected chip      (● chip)  selected chip
[−] 5 [+]       NumberStepper
════            sticky bar edge
{Census}        SourceBadge
₹1.2 lakh·      FigureChip (tap → FigureSheet)
▓▓▓             skeleton
```

**Emoji in these frames stand in for Lucide icons** (🥛 = `Milk`, 🏛 = `Landmark`, etc.; the mapping is in `ui-ux.md` §2.5). Never use emoji in the real UI.

Screen index:

| # | Route | Screen |
|---|---|---|
| 1 | `/` | Home |
| 2 | `/login` | Login |
| 3–7 | `/new` | Intake wizard (describe, steps 1–4) |
| 8–10 | `/new` | Building the DPR (normal, retrying, failed) |
| 11–15 | `/reports/:id` | Report (Explanation, FigureSheet, Numbers, Bank DPR, unavailable explanation) |
| 16 | `/reports/:id` | What-if sheet |
| 17 | `/reports/:id` | Ask (chat) sheet |
| 18–19 | `/compare` | Comparison picker + result |
| 20–21 | `/reports` | My Reports (list, empty) |
| 22 | any | Menus, offline banner, loading skeleton |

---

## 1. Home `/`

```
┌────────────────────────────────────┐
│ ◆ Requiem              म ▾   ◯     │  [AppBar] language · account
├────────────────────────────────────┤
│                                    │
│  Will your business work           │  h1
│  in your village?                  │
│                                    │
│  Get a bank-ready project report   │  body
│  and a loan plan, explained in     │
│  Marathi, Hindi or English.        │
│                                    │
│  ┌──────────────────────────────┐  │
│  │  [SVG: village shop + cow]   │  │  illustration, inline SVG
│  └──────────────────────────────┘  │
│                                    │
│  ── The 3 questions we answer ──   │  h2
│  ┌──────────────────────────────┐  │
│  │ ⌖ Will it work here?         │  │  icon + line each
│  │ ₹ How much money do I need?  │  │
│  │ 🏛 Which govt loan, what EMI? │  │  (Lucide Landmark, not emoji)
│  └──────────────────────────────┘  │
│                                    │
│  ── How it works ──                │
│  ① Tell us your village & idea     │
│  ② We check market, cost, schemes  │
│  ③ Get your DPR + simple advice    │
│                                    │
│  ── Why trust it ──                │
│  ✓ Every number shows its source   │
│  ✓ Real govt schemes, dated        │
│  ✓ Bank document you can share     │
│                                    │
│  ── What you get ──  (2×2 grid)    │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ ▤ Report    │ │ ⇅ Try       │   │
│  │   & charts  │ │   changes   │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ ⚖ Compare   │ │ अ 3         │   │
│  │ businesses  │ │ languages   │   │
│  └─────────────┘ └─────────────┘   │
│                                    │
│  ── Schemes covered ──             │
│  (MUDRA)(PMEGP)(Stand-Up India)    │  chips, wrap
│  (PM Vishwakarma)(CMEGP)(KCC)      │
│                                    │
│  ── Team ──                        │
│  3 names · roles                   │
│                                    │
│  Indicative only. Verify with      │  caption
│  your bank.                        │
├════════════════════════════════════┤
│ [■  Start my DPR — free         ]  │  [BottomActionBar] sticky
└────────────────────────────────────┘
```

**Desktop ≥1024:** two-column hero (text left, illustration right), with the CTA inline in the hero instead of a sticky bar. The other sections sit in a 960 px column, and "What you get" becomes a 4-column row.

---

## 2. Login `/login`

```
┌────────────────────────────────────┐
│ ‹ Back                 म ▾         │
├────────────────────────────────────┤
│                                    │
│  Save your reports                 │  h1
│  Log in to see your DPRs later.    │
│                                    │
│  ┌─────────────┬──────────────┐    │  [Tabs]
│  │  Log in  ▔▔ │ Create account│   │
│  └─────────────┴──────────────┘    │
│                                    │
│  Username                          │  label
│  ┌──────────────────────────────┐  │
│  │                              │  │  autocomplete=username
│  └──────────────────────────────┘  │
│  Password                          │
│  ┌──────────────────────────┬───┐  │
│  │ ••••••••                 │ 👁 │  │  show/hide toggle (Eye icon)
│  └──────────────────────────┴───┘  │
│  ⚠ Wrong username or password.     │  error under field (when shown)
│                                    │
│  [■  Log in                     ]  │
│                                    │
│  ──────────── or ────────────      │
│                                    │
│  [□  Continue without account   ]  │  guest, large
│  You can still build and share     │  caption
│  reports.                          │
└────────────────────────────────────┘
```

**Desktop:** a centred 400 px card.

---

## 3. Wizard: describe in your own words (optional, top of `/new`)

```
┌────────────────────────────────────┐
│ ‹ Back      New DPR    म ▾         │
├────────────────────────────────────┤
│  Step 1 of 4                       │  [Stepper]
│  ▰▱▱▱                              │
│                                    │
│  ┌──────────────────────────────┐  │  collapsible card, open by default
│  │ 💬 Tell us in your own words  │  │  (MessageCircle icon)
│  │ ┌──────────────────────────┐ │  │
│  │ │ मला ५ म्हशींचा दुग्ध व्यवसाय │ │  │  textarea
│  │ │ सुरू करायचा आहे...         │ │  │
│  │ └──────────────────────────┘ │  │
│  │ [□ 🎤 Speak]  [□ Fill for me]│  │  mic = stretch
│  └──────────────────────────────┘  │
│  ───────── or choose below ─────── │
│                                    │
│  Where will you run it?            │  h2 (step 1 content continues → frame 4)
```

After "Fill for me": a loading button, then the steps are pre-filled and each pre-filled step shows:
```
│ ┌──────────────────────────────┐   │
│ │ ✎ Filled from what you said. │   │  --primary-soft banner
│ │   Please check.              │   │
│ └──────────────────────────────┘   │
```

---

## 4. Wizard step 1: Where

```
┌────────────────────────────────────┐
│ ‹ Back      New DPR    म ▾         │
├────────────────────────────────────┤
│  Step 1 of 4                       │
│  ▰▱▱▱                              │
│                                    │
│  Where will you run it?            │  h1
│                                    │
│  District                          │
│  ┌──────────────────────────────┐  │
│  │ ⌖ Nashik                   ▾ │  │  opens searchable picker sheet
│  └──────────────────────────────┘  │
│  Block (taluka)                    │
│  ┌──────────────────────────────┐  │
│  │ ⌖ Niphad                   ▾ │  │
│  └──────────────────────────────┘  │
│  Village                           │
│  ┌──────────────────────────────┐  │
│  │ ⌖ Choose village           ▾ │  │  enabled after block
│  └──────────────────────────────┘  │
│                                    │
│  ┌──────────────────────────────┐  │  appears after village chosen
│  │ Lasalgaon · 4,812 homes      │  │
│  │ {Census 2011, projected}     │  │
│  └──────────────────────────────┘  │
├════════════════════════════════════┤
│ [■  Next                        ]  │  disabled until village chosen
│   Choose a village first           │  reason caption when disabled
└────────────────────────────────────┘
```

**Village picker sheet:**
```
┌────────────────────────────────────┐
│            ───                     │  grab handle
│  Choose village               ✕    │
│  ┌──────────────────────────────┐  │
│  │ 🔍 Search village            │  │
│  └──────────────────────────────┘  │
│  Lasalgaon                         │  48px rows
│  Pimpalgaon Baswant                │
│  Vinchur                           │
│  Ozar                              │
│  …                                 │
└────────────────────────────────────┘
```

---

## 5. Wizard step 2: Business

```
┌────────────────────────────────────┐
│ ‹ Back      New DPR    म ▾         │
├────────────────────────────────────┤
│  Step 2 of 4                       │
│  ▰▰▱▱                              │
│                                    │
│  What business?                    │  h1
│                                    │
│  ┌──────────────┐ ┌──────────────┐ │  [ChoiceCard] 2×3 radiogroup
│  │      🥛      │ │      🌱      │ │  (Lucide Milk / Sprout)
│  │    Dairy  ✓  │ │    Onion     │ │  selected = soft fill + border + ✓
│  │              │ │   farming    │ │
│  └──────────────┘ └──────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ │
│  │      🥚      │ │      ✂       │ │  Egg / Scissors
│  │   Poultry    │ │  Tailoring   │ │
│  └──────────────┘ └──────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ │
│  │      🏪      │ │      🌾      │ │  Store / Wheat
│  │    Kirana    │ │  Flour mill  │ │
│  └──────────────┘ └──────────────┘ │
│                                    │
│  How many animals?                 │  label from archetype.unit_label
│  ┌──────────────────────────────┐  │  [NumberStepper]
│  │  [ − ]      5 animals   [ + ]│  │
│  └──────────────────────────────┘  │
│  Most start with 3 to 6.           │  helper
├════════════════════════════════════┤
│ [■  Next                        ]  │
└────────────────────────────────────┘
```

---

## 6. Wizard step 3: Money

```
┌────────────────────────────────────┐
│ ‹ Back      New DPR    म ▾         │
├────────────────────────────────────┤
│  Step 3 of 4                       │
│  ▰▰▰▱                              │
│                                    │
│  How much of your own money        │  h1
│  can you put in?                   │
│                                    │
│  Your own money                    │  label
│  ┌──────────────────────────────┐  │  [MoneyInput] inputmode=numeric
│  │ ₹  1,00,000                  │  │
│  └──────────────────────────────┘  │
│  ₹1 lakh                           │  words line, live
│                                    │
│  ( ₹25k ) ( ₹50k ) (● ₹1L ) ( ₹2L )│  quick chips
│                                    │
│  ┌──────────────────────────────┐  │
│  │ ⓘ A bank usually expects you │  │  --primary-soft info
│  │   to put in some money       │  │
│  │   yourself. We'll show       │  │
│  │   exactly how much.          │  │
│  └──────────────────────────────┘  │
├════════════════════════════════════┤
│ [■  Next                        ]  │
└────────────────────────────────────┘
```

---

## 7. Wizard step 4: About you

Only the fields the Archetype needs (dairy shown).

```
┌────────────────────────────────────┐
│ ‹ Back      New DPR    म ▾         │
├────────────────────────────────────┤
│  Step 4 of 4                       │
│  ▰▰▰▰                              │
│                                    │
│  About you                         │  h1
│  These decide which govt schemes   │  helper
│  you can get.                      │
│                                    │
│  Age                               │
│  ┌──────────────────────────────┐  │
│  │  [ − ]       32 years   [ + ]│  │
│  └──────────────────────────────┘  │
│                                    │
│  You are                           │
│  (● Woman ) ( Man ) ( Other )      │  [ChipGroup]
│                                    │
│  Category                          │
│  ( General ) (● OBC ) ( SC ) ( ST )│
│                                    │
│  Schooling                         │
│  ( None ) ( Below 8th ) ( 8th )    │  wraps
│  (● 10th ) ( 12th ) ( Graduate )   │
│                                    │
│  Is this a new business?           │
│  (● New ) ( Already running )      │
│                                    │
│  Got a govt subsidy before?        │
│  ( Yes ) (● No )                   │
│                                    │
│  Repaid a MUDRA Tarun loan?        │
│  ( Yes ) (● No )                   │
│                                    │
│  ⚠ Please choose your category.    │  inline error example
├════════════════════════════════════┤
│ [■  Build my DPR                ]  │
└────────────────────────────────────┘
```

---

## 8. Building the DPR (StageTrace)

```
┌────────────────────────────────────┐
│            Building your DPR       │  no back while running
├────────────────────────────────────┤
│                                    │
│  Dairy · Lasalgaon · ₹1 lakh       │  summary line
│                                    │
│  ✓ Reading your details     0.1s   │  [StageTrace] done
│  ✓ Your village market      0.2s   │
│      {Census} {Map}                │  source chips
│  ✓ Total money needed       0.1s   │
│      {Our estimate}                │
│  ✓ Govt loan schemes        0.1s   │
│      {Govt scheme · checked 1 Oct} │
│  ✓ Bank report (DPR)        0.2s   │
│  ◌ Writing simple advice…          │  running spinner
│                                    │
│  ┌──────────────────────────────┐  │
│  │ All numbers come from our    │  │  muted caption card
│  │ calculator, not the AI.      │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

## 9. Building: retrying (self-correction visible)

```
│  ✓ Bank report (DPR)        0.2s   │
│  ↻ Re-checking numbers…            │  amber row, RefreshCw icon
│    The advice had a number we      │  caption
│    didn't calculate. Rewriting.    │
```
Then it becomes `✓ Writing simple advice   6.4s · checked`, and the report opens after 600 ms.

## 10. Building: failed

```
│  ✓ Total money needed       0.1s   │
│  ✕ Govt loan schemes               │  --bad row
│    Something went wrong on our     │
│    side.                           │
│    [□ Try again ]                  │
```

---

## 11. Report: Explanation tab (default) `/reports/:id`

```
┌────────────────────────────────────┐
│ ‹ My reports   Dairy   म ▾   ◯     │
├────────────────────────────────────┤
│ ┌────────────────────────────────┐ │  [VerdictCard] --ok-soft
│ │ ✓ Good to start                │ │  icon + plain label
│ │ Profit covers the EMI 1.6×     │ │  worst-signal line
│ │                                │ │
│ │  Loan          Monthly EMI     │ │
│ │  ₹2.4 lakh·    ₹5,120·         │ │  hero figures (FigureChips)
│ │                                │ │
│ │  🏛 MUDRA Kishore               │ │
│ └────────────────────────────────┘ │
│ ┌──────────┬─────────┬───────────┐ │  [Tabs] sticky
│ │Explanation│ Numbers │ Bank DPR │ │
│ │ ▔▔▔▔▔▔▔▔ │         │           │ │
│ └──────────┴─────────┴───────────┘ │
│  🛡 12 of 12 numbers checked  🔊 Listen│  ShieldCheck badge · Listen (stretch)
│                                    │
│  Is it a good idea?                │  h2
│  Yes. Lasalgaon's milk centre      │  body with FigureChips
│  buys all you produce. With        │
│  5 animals you make about          │
│  ₹9,800· a month after costs,      │
│  enough to pay the EMI.            │
│                                    │
│  Your village market               │
│  4,812· homes. The cooperative     │
│  collects milk daily …             │
│                                    │
│  Money plan                        │
│  Total needed ₹3.4 lakh·. You put  │
│  in ₹1 lakh·, borrow ₹2.4 lakh·.   │
│  EMI starts after 6· months.       │
│                                    │
│  Good                 Watch out    │  SWOT as two lists
│  • Sure buyer         • Feed price │  (stack on <360)
│  • Your experience    • Animal     │
│                         illness    │
│                                    │
│  Pricing tips                      │
│  …                                 │
│                                    │
│  Next steps                        │
│  ① Visit the bank branch in Niphad │
│  ② Carry: Aadhaar, PAN, …          │
│  ③ Show this DPR                   │
│                                    │
│  [□ Compare with another business] │
│                                    │
│  Indicative only. Verify with      │
│  your bank.                        │
├════════════════════════════════════┤
│ [□ ⇅ Try changes ] [□ 💬 Ask     ] │  [BottomActionBar] two secondary
└────────────────────────────────────┘
```

**Not feasible variant:** the VerdictCard uses `--bad-soft` with `✕ Not advisable right now`, a reason line like "Profit doesn't cover the EMI", and a link **"See how to make it work ↓"** that scrolls to:
```
│  How to make it work               │  Path to Yes
│  ┌──────────────────────────────┐  │
│  │ Put in ₹40,000· more         │  │
│  │ → Good to start  [□ Try it ] │  │  opens What-if with value set
│  ├──────────────────────────────┤  │
│  │ Start with 3· animals        │  │
│  │ → Good to start  [□ Try it ] │  │
│  └──────────────────────────────┘  │
```

**Desktop ≥1024:** the VerdictCard and tabs sit in a 720 px column, and a 360 px right panel shows What-if inline. Ask opens as a right drawer.

---

## 12. FigureSheet (tap any `·` figure)

```
┌────────────────────────────────────┐
│            ───                     │
│  Why this number?             ✕    │
│                                    │
│  Monthly EMI                       │  plain label
│  ₹5,120                            │  hero, exact
│                                    │
│  How we calculated it              │  h3
│  Loan amount spread over the       │  formula in words
│  repayment months, with interest.  │
│                                    │
│  Loan          ₹2,40,000 {Calculated}│
│  Interest      10% a year {Govt scheme}│
│  Months        54         {Govt scheme}│
│                                    │
│  ⓘ Bank sets the final rate.       │  note
└────────────────────────────────────┘
```
Assumption variant: add a dotted card that says "This is our estimate. If you know better, change it in Try changes." with a `[□ Try changes]` button.

---

## 13. Report: Numbers tab

```
│ ┌──────────┬─────────┬───────────┐ │
│ │Explanation│ Numbers │ Bank DPR │ │
│ │           │ ▔▔▔▔▔▔▔ │          │ │
│ └──────────┴─────────┴───────────┘ │
│  Where the money comes from        │  h2
│  ┌──────────────────────────────┐  │  stacked horizontal bar
│  │█████████░░░░░░░░░░░░░░░░░░░░│  │
│  │ You ₹1L   Loan ₹2.4L         │  │  direct labels
│  └──────────────────────────────┘  │
│  [ Show as table ]                 │  ghost toggle
│                                    │
│  Total money needed                │
│  Animals      ▇▇▇▇▇▇▇▇▇  ₹2.0L     │  horizontal bars, sorted
│  Shed         ▇▇▇        ₹0.9L     │
│  Working cap. ▇▇         ₹0.5L     │
│                                    │
│  Profit each year (5 years)        │
│   ▁▃▅▆▇   columns, labelled        │
│                                    │
│  Key numbers                       │  [MetricRows]
│  Can profit pay EMI?   1.6× ✓      │
│                        {Calculated}│
│  Profit starts         Month 4     │
│  Money back in         28 months   │
│  Homes in village      4,812       │
│                        {Census}    │
│  Similar shops nearby  2           │
│                  {Map · few mapped}│
```

---

## 14. Report: Bank DPR tab

```
│ ┌──────────┬─────────┬───────────┐ │
│ │Explanation│ Numbers │ Bank DPR │ │
│ │           │         │ ▔▔▔▔▔▔▔▔ │ │
│ └──────────┴─────────┴───────────┘ │
│  [□ ⤴ Share ]  [□ ⬇ Download PDF ] │  Web Share · print
│                                    │
│  DETAILED PROJECT REPORT           │  English, document style
│  Dairy unit · Lasalgaon, Niphad    │
│  Prepared 11 Oct 2026              │
│  ────────────────────────────────  │
│  1. Entrepreneur profile           │
│  2. Project summary                │  collapsible sections on mobile
│  3. Market analysis           ▾    │  (all expanded in print)
│  4. Project cost              ▾    │
│     Animals (5)      2,00,000      │  MetricRows on mobile,
│     Shed               90,000      │  real tables in print
│     Working capital    50,000      │
│     Total            3,40,000      │
│  5. Means of finance          ▾    │
│  6. Scheme terms              ▾    │
│  7. Repayment schedule        ▾    │  first 12 rows + "Show all 60"
│  8. 5-year projections        ▾    │
│  9. Break-even                ▾    │
│ 10. DSCR                      ▾    │
│ 11. SWOT & risks              ▾    │
│ 12. Documents checklist       ▾    │
│                                    │
│  Sources: Census 2011; OSM;        │
│  scheme pages verified 1 Oct 2026. │
```

**Print (A4):** no AppBar, tabs, bars or buttons. All sections expanded, real tables, a page break before §7 and §8, and a footer with the report id and date on each page.

---

## 15. Explanation unavailable (LLM failed)

```
│ ┌──────────────────────────────┐   │
│ │ ⚠ We couldn't write the      │   │  --warn-soft banner
│ │   simple advice right now.   │   │
│ │   All numbers are complete.  │   │
│ │   [□ Try again ]             │   │
│ └──────────────────────────────┘   │
│  Key numbers  (MetricRows shown)   │
```

---

## 16. What-if sheet (Try changes)

```
┌────────────────────────────────────┐
│            ───                     │
│  Try changes                  ✕    │
│ ┌────────────────────────────────┐ │  pinned result strip
│ │ 🏛 MUDRA Tarun   Loan ₹5.9L     │ │
│ │ EMI ₹12,400      ⚠ With changes│ │
│ │ ↻ Changed: Kishore → Tarun     │ │  pulses once on flip
│ └────────────────────────────────┘ │
│                                    │
│  Your own money                    │
│  ┌──────────────────────────────┐  │
│  │ ₹  1,00,000                  │  │
│  └──────────────────────────────┘  │
│  ○━━━━━●━━━━━━━━━━━━━━━━━━━━━━━○   │  slider
│  [ − ₹5,000 ]          [ + ₹5,000 ]│  steppers (drag alternative)
│                                    │
│  Number of animals                 │
│  [ − ]        10 animals     [ + ] │
│  ○━━━━━━━━━━━●━━━━━━━━━━━━━━━━━○   │
│                                    │
│  Repay over                        │
│  ( 3 yrs ) (● 5 yrs ) ( 7 yrs )    │
│                                    │
├════════════════════════════════════┤
│ [ Reset ]   [■  Use these numbers ]│  ghost + primary (new DPR)
└────────────────────────────────────┘
```

**Desktop:** the same content shows permanently in the right panel. "Use these numbers" stays primary.

---

## 17. Ask (chat) sheet

```
┌────────────────────────────────────┐
│            ───                     │
│  Ask about your DPR           ✕    │
│                                    │
│  ( Which documents do I need? )    │  suggestion chips (empty state)
│  ( What if I start smaller? )      │
│  ( Why not PMEGP? )                │
│                                    │
│            ┌─────────────────────┐ │
│            │ Why not PMEGP?      │ │  user bubble (right)
│            └─────────────────────┘ │
│ ┌─────────────────────────────┐    │
│ │ PMEGP is only for new units │    │  assistant bubble (left)
│ │ above ₹… Your project cost  │    │
│ │ ₹3.4 lakh· qualifies, but   │    │  FigureChips inside
│ │ MUDRA has lower paperwork.  │    │
│ │ {Govt scheme · PMEGP} ↗     │    │  citation badge → source
│ └─────────────────────────────┘    │
│ ┌─────────────────────────────┐    │
│ │ Suggested: 3 animals        │    │  suggested change card
│ │ → Good to start [□ Try this]│    │  opens What-if prefilled
│ └─────────────────────────────┘    │
│                                    │
├════════════════════════════════════┤
│ ┌──────────────────────┐ 🎤  [➤]   │  input · mic (stretch) · send
│ │ Type your question   │           │
│ └──────────────────────┘           │
└────────────────────────────────────┘
```
While waiting: an assistant bubble with three animated dots, label "Thinking…" (static under reduced motion).

---

## 18. Comparison: pick `/compare`

```
┌────────────────────────────────────┐
│ ‹ Report    Compare    म ▾         │
├────────────────────────────────────┤
│  Compare with Dairy                │  h1
│  Same village, same ₹1 lakh.       │
│  Pick 1 or 2 more.                 │
│                                    │
│  ┌──────────────┐ ┌──────────────┐ │  ChoiceCards, multi-select (max 2)
│  │ 🥛 Dairy      │ │ 🌱 Onion   ✓ │ │  current = locked, labelled
│  │   (current)  │ │   farming    │ │
│  └──────────────┘ └──────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ │
│  │ 🥚 Poultry    │ │ ✂ Tailoring  │ │
│  └──────────────┘ └──────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ │
│  │ 🏪 Kirana     │ │ 🌾 Flour mill│ │
│  └──────────────┘ └──────────────┘ │
├════════════════════════════════════┤
│ [■  Compare                     ]  │
└────────────────────────────────────┘
```

## 19. Comparison: result

```
┌────────────────────────────────────┐
│ ‹ Report    Compare    म ▾         │
├────────────────────────────────────┤
│                 Dairy     Onion    │  [MetricRows] column heads
│  Verdict       ✓ Good    ⚠ Changes │  icon + word
│  Loan          ₹2.4L     ₹1.1L ✓   │  ✓ = better (with sr text)
│  EMI / payment ₹5,120 ✓  ₹1.3L once│
│                          at harvest│
│  Profit pays   1.6× ✓    1.2×      │
│  EMI?                              │
│  Money back    28 mo     14 mo ✓   │  (values illustrative)
│  Scheme        MUDRA     KCC       │
│  Market        Milk      Lasalgaon │
│                centre    APMC      │
│                                    │
│  Can profit pay EMI?               │  horizontal bar chart
│  Dairy  ▇▇▇▇▇▇▇▇ 1.6×              │
│  Onion  ▇▇▇▇▇▇   1.2×              │
│                                    │
│  Which suits you?                  │  LLM paragraph, FigureChips
│  Dairy gives steady monthly        │
│  income; onion pays once a         │
│  season and depends on price …     │
│                                    │
│  [□ Open full DPR: Onion ]         │
└────────────────────────────────────┘
```

---

## 20. My Reports `/reports`

```
┌────────────────────────────────────┐
│ ‹ Home    My reports   म ▾   ◯     │
├────────────────────────────────────┤
│  ┌──────────────────────────────┐  │  list cards, 72px+
│  │ 🥛 Dairy · Lasalgaon          │  │
│  │ ✓ Good to start · 11 Oct     ›│  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ 🌱 Onion · Lasalgaon          │  │
│  │ ⚠ With changes · 11 Oct      ›│  │
│  └──────────────────────────────┘  │
├════════════════════════════════════┤
│ [■  Build a new DPR             ]  │
└────────────────────────────────────┘
```

## 21. My Reports: empty

```
│                                    │
│            📄                      │  FileText icon, 48px
│     No saved reports yet           │
│  Reports you build while logged    │
│  in appear here.                   │
│                                    │
│  [■  Build your first DPR       ]  │
```

---

## 22. Menus and states

**Language menu** (from `म ▾`):
```
│  ┌───────────────┐                 │
│  │ English       │                 │  each in its own script
│  │ हिंदी          │                 │
│  │ ● मराठी        │                 │
│  └───────────────┘                 │
```

**Account menu:** logged in shows `My reports · Log out` (Log out separated by a divider). A guest sees `Log in to save reports`.

**Offline banner** (top, under the AppBar, all screens):
```
│ ⚠ No internet. Saved reports still │  --warn-soft
│   open.                            │
```

**Loading skeleton** (report page while fetching):
```
│ ┌────────────────────────────────┐ │
│ │ ▓▓▓▓▓▓▓▓▓▓▓                    │ │  VerdictCard shape
│ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓             │ │
│ │ ▓▓▓▓▓▓▓      ▓▓▓▓▓▓▓           │ │
│ └────────────────────────────────┘ │
│ ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓  ▓▓▓▓▓▓▓          │  tabs
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓        │  text lines
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓              │
```

**Toast:** sits above the bottom bar: `✓ Link copied`, auto-dismisses after 4 s.

---

## Demo path through the frames

1 → 3 (Marathi describe, Fill for me) → 4 → 5 → 6 → 7 → 8 (and 9 if a retry happens) → 11 → 12 (tap EMI) → 16 (raise to 10 animals, Kishore → Tarun flip) → 18 → 19 (dairy vs onion) → 14 (Share, Download PDF). Run it in Chrome DevTools at a 360 px device frame.
