# UI/UX Spec

Design system and interaction rules for `web/`. Screens are drawn in [`wireframes.md`](wireframes.md). Product scope: [`prd.md`](prd.md). Technical notes: [`trd.md`](trd.md) §8. Vocabulary: [`CONTEXT.md`](../CONTEXT.md).

**Design for:** a first-time rural Entrepreneur on a budget Android phone (360–412 px wide, 2–4 GB RAM), often outdoors, on patchy mobile data, more comfortable in Marathi or Hindi than English, possibly with limited reading confidence. **Desktop is secondary**, mainly the judges' projector.

---

## 1. Principles

1. **Answer first, details later.** Every screen leads with the one thing the Entrepreneur needs: the Verdict, the loan amount, the EMI. Charts, tables and the bank document come after.
2. **One job per screen, one primary button.** The amber button is the next step. Everything else is visually quieter.
3. **Tap, don't type.** Prefer cards, chips, steppers and pickers over text fields. The only free-text inputs are the "describe it" box and login.
4. **Every option has an icon and a word.** Icons help readers with limited reading confidence; words remove ambiguity. Never an icon alone, never colour alone.
5. **Plain words in the Entrepreneur's language.** Bank jargon appears only in the Bank DPR tab. Elsewhere, "DSCR" becomes "Can your profit pay the EMI?"
6. **Money the way people say it.** ₹1,20,000 is shown as "₹1.2 lakh" in headlines, with the exact amount in the figure sheet.
7. **Honest about where numbers come from.** Every number has a Source Badge and opens a "Why this number?" sheet. Trust comes from showing, not claiming.
8. **Works on a slow phone and a slow network.** Light pages, no heavy animation, skeletons instead of blank screens, and clear offline and retry states.

## 2. Design tokens

All colours are CSS variables on `:root`. Components use tokens through Tailwind, never raw hex. Light theme only for now; the tokens make a dark theme possible later. Contrast values were checked against WCAG; body text exceeds 7:1 for sunlight readability.

### 2.1 Colour

| Token | Hex | Use | Contrast |
|---|---|---|---|
| `--bg` | `#FAFAF7` | Page background (warm off-white) | — |
| `--surface` | `#FFFFFF` | Cards, sheets, app bar | — |
| `--surface-soft` | `#F1F4F1` | Inset areas, table stripes, chip default | — |
| `--text` | `#1C2421` | Body and headings | 15:1 on `--bg` |
| `--text-muted` | `#4B5753` | Helper text, captions | 7.2:1 on `--bg` |
| `--border` | `#D3DAD5` | Dividers, card outlines (decorative) | — |
| `--border-strong` | `#7A857F` | Input borders, unselected chip outlines (must be visible) | 3.6:1 on `--surface` |
| `--primary` | `#0F6E56` | Brand, links, selected state, active tab | white text 6.2:1 |
| `--primary-soft` | `#E3F1EC` | Selected card fill, info banners | `--primary` text 5.6:1 |
| `--on-primary` | `#FFFFFF` | Text on primary | — |
| `--cta` | `#F2A900` | **The one primary action button per screen** | `--text` on it 7.8:1 |
| `--cta-pressed` | `#D99700` | Pressed CTA | — |
| `--ring` | `#0F6E56` | Focus ring, 3 px, 2 px offset | 6.2:1 on white |
| `--ok` | `#1B7A3D` | Verdict feasible | white 5.4:1 |
| `--ok-soft` | `#E7F4EC` | Feasible card fill | `--ok` text 4.9:1 |
| `--warn` | `#B45309` | Feasible with changes, retrying | white 5.0:1 |
| `--warn-soft` | `#FDF0E1` | Warn card fill | `--warn` text 4.6:1 |
| `--bad` | `#B42318` | Not feasible, errors | white 6.6:1 |
| `--bad-soft` | `#FDE8E6` | Error card fill | `--bad` text 5.6:1 |

**Chart series** (distinct for common colour-blindness types, always with labels): `#0F6E56` teal, `#E09B00` amber, `#2F6FDB` blue, `#8A948F` grey.

### 2.2 Typography

- **Family:** **Mukta** (Latin + Devanagari, by Ek Type), self-hosted with `@fontsource/mukta` (weights 400, 500, 600, 700) so it works offline. Fallback: `system-ui, "Noto Sans Devanagari", sans-serif`.
- **Line height:** 1.6 for body (Devanagari needs room for matras), 1.25 for headings.
- **Numbers:** `font-variant-numeric: tabular-nums` in tables, figure chips and the what-if strip.
- **Minimum size 14 px**, and only for captions. Body text is 16 px.

| Token | Size / weight | Use |
|---|---|---|
| `text-hero` | 40 / 700 | The big number on the Verdict card (loan or EMI) |
| `text-h1` | 28 / 700 | Screen title |
| `text-h2` | 22 / 600 | Section title |
| `text-h3` | 18 / 600 | Card title |
| `text-body` | 16 / 400 | Body |
| `text-label` | 16 / 500 | Buttons, input labels, tabs |
| `text-caption` | 14 / 400 | Helper text, Source Badges, timings |

### 2.3 Spacing, shape, elevation

- **Spacing scale (px):** 4, 8, 12, 16, 24, 32, 48. Screen gutter 16 on mobile, 24 from 768 px.
- **Radius:** 12 for cards and sheets, 10 for buttons and inputs, full for chips and badges.
- **Elevation:** one shadow for sheets and the sticky bars (`0 -2px 12px rgb(0 0 0 / 0.08)`). Cards use a border, not a shadow.
- **Touch targets:** **48 × 48 px minimum** (larger than the 44 px guideline, for less precise taps), with at least 8 px between targets.
- **z-index:** content 0 · sticky tabs 10 · sticky bottom bar 20 · sheet scrim 40 · sheet 50 · toast 60.

### 2.4 Motion

- Press feedback within 100 ms: background darken, no scale (scale jitters on low-end phones).
- Sheets slide up in 220 ms, decelerate; close in 160 ms.
- Stage trace: each stage fades its icon from grey to colour in 200 ms.
- What-if flip: the changed item pulses once (opacity 1 → 0.6 → 1, 400 ms).
- Under `prefers-reduced-motion`, everything becomes instant.
- **Animate only `transform` and `opacity`.**

### 2.5 Icons

**Lucide** (bundled with shadcn/ui), 24 px, 2 px stroke, outline style everywhere. Decorative icons beside text get `aria-hidden="true"`; icon-only buttons get an `aria-label`.

| Concept | Icon |
|---|---|
| Dairy · Onion cultivation · Poultry · Tailoring · Kirana · Flour mill | `Milk` · `Sprout` · `Egg` · `Scissors` · `Store` · `Wheat` |
| Source: census · osm · user · assumption · scheme · computed | `Users` · `MapPin` · `Pencil` · `Lightbulb` · `Landmark` · `Calculator` |
| Verdict: feasible · with changes · not feasible | `CircleCheck` · `TriangleAlert` · `CircleX` |
| Language · Account · Back · Share · Download · Listen · Mic · Ask · Try changes | `Languages` · `CircleUser` · `ChevronLeft` · `Share2` · `Download` · `Volume2` · `Mic` · `MessageCircle` · `SlidersHorizontal` |

## 3. Layout and breakpoints

| Width | Layout |
|---|---|
| **< 768 (primary)** | Single column, 16 px gutter. Top app bar 56 px. Sticky bottom action bar 72 px plus safe-area inset. Sheets for what-if, chat, figure details |
| 768 – 1023 | Single column, max 640 px, centred, 24 px gutter |
| ≥ 1024 | Report: 720 px main column + 360 px right panel (what-if inline; chat as a right drawer). Home: two-column hero. Wizard stays a centred 560 px column |

- `min-h-dvh` (not `100vh`). The viewport meta never disables zoom.
- Fixed bars reserve padding so content never hides behind them. Use `env(safe-area-inset-bottom)` on the bottom bar.
- No horizontal scroll anywhere. Tables reflow to metric rows (§4.10).
- `overscroll-behavior: contain` on sheets to stop accidental pull-to-refresh.

## 4. Components

shadcn/ui primitives, restyled with the tokens. Names match the files in `web/src/components/`.

### 4.1 AppBar
Logo + product name on the left. On the right: **language switch** (shows `EN` / `हि` / `म`, opens a menu with each language written in its own script) and an account icon (menu: My Reports, Log out; guest: Log in). On inner screens a Back chevron replaces the logo. Height 56 px, `--surface`, bottom border.

### 4.2 Button
- **Primary:** `--cta` fill, `--text` label, 48 px tall, full width on mobile. Only one per screen.
- **Secondary:** `--surface` fill, `--primary` border and label.
- **Ghost:** text only, `--primary`.
- **Loading:** spinner + label "Working…", disabled, keeps its width.
- **Disabled:** 45% opacity, `aria-disabled`, with a reason shown below ("Choose a village first").

### 4.3 BottomActionBar
Sticky at the bottom, `--surface`, top shadow. Holds the screen's primary button, or on the report page two equal buttons: **Try changes** (secondary) and **Ask** (secondary). Hidden while the keyboard is open.

### 4.4 Stepper (wizard progress)
"Step 2 of 4" text + a 4-segment bar. Each segment shows done (`--primary`), current (`--primary` outline) or upcoming (`--border`). Back is in the AppBar. Tapping a done segment jumps back to that step.

### 4.5 ChoiceCard
A large tappable card (min 96 px tall), icon at 32 px plus a label, used for Archetypes in a 2-column grid. When selected: `--primary-soft` fill, 2 px `--primary` border and a check icon in the corner. `role="radio"` inside a `radiogroup`.

### 4.6 Chip / ChipGroup
48 px tall, pill-shaped. Used for eligibility answers (Gender, Category, Education, yes/no questions) and money shortcuts. Single-select uses `radiogroup` semantics. Wraps to new lines; never scrolls sideways.

### 4.7 NumberStepper
A large value display with −/+ buttons (48 px each) and the unit label ("5 animals"). An optional slider sits underneath. Every slider has steppers, so dragging is never the only way. The value is announced via `aria-live="polite"`.

### 4.8 MoneyInput
A labelled `₹` field, `inputmode="numeric"`, that groups digits live in Indian style (1,00,000). Below it, a words line: "₹1 lakh" / "₹1 लाख". Quick chips: ₹25k, ₹50k, ₹1L, ₹2L.

### 4.9 VerdictCard
Sits at the top of the report, always visible above the tabs.
- Soft verdict fill (`--ok-soft` / `--warn-soft` / `--bad-soft`).
- Verdict icon + **plain label** (see §6.2).
- One line on why: the worst signal, in words.
- Two hero figures side by side: **Loan** and **Monthly EMI**.
- The matched Scheme name.

When the Verdict isn't feasible, a "See how to make it work" link jumps to the Path to Yes section.

### 4.10 MetricRows (replaces tables on mobile)
Each row has a label on the left and the value(s) on the right. With 2–3 columns (Comparison), each value cell is at least 88 px. The better value gets a `Check` icon and the text "better", never colour alone. Used for Comparison, repayment summary and the Bank View on small screens.

### 4.11 FigureChip and FigureSheet
- **FigureChip:** an inline number inside Entrepreneur View text, using the language's digits and lakh formatting. It has a dotted `--primary` underline and a small source icon, and is a `button`.
- **FigureSheet** (opens on tap):
  - heading "Why this number?"
  - big value
  - plain label
  - "How we calculated it": the formula in words, with each input listed with its own value and Source Badge
  - the note, if any
  - for an Assumption: "This is our estimate. If you know better, change it in Try changes."

### 4.12 SourceBadge
A pill with an icon and a word: **Census** · **Map** (OSM) · **You entered** · **Our estimate** · **Govt scheme** · **Calculated**. Neutral `--surface-soft` fill with `--text-muted` text. An Assumption also shows a dotted outline so estimates stand out. When OSM coverage is low, add "few shops are mapped; please confirm".

### 4.13 StageTrace
A vertical list of 6 rows: Intake, Your village, Cost, Loan schemes, DPR, Explanation.
- **Row states:** waiting (grey icon), running (spinner), done (`CircleCheck` + duration + source chips), retrying (amber `RefreshCw` + "Re-checking numbers…"), failed (`CircleX` + retry button).
- Announced through a polite live region.

### 4.14 Sheet
A bottom sheet on mobile, right panel or drawer on desktop. It has a grab handle, title, close button (48 px, labelled) and a scrim (`rgb(0 0 0 / 0.45)`). Close it by swiping down, tapping the scrim, pressing Esc, or the close button. Focus is trapped inside and returns to the trigger when it closes.

### 4.15 Tabs
Sticky under the VerdictCard: **Explanation · Numbers · Bank DPR**. 48 px tall, the active tab has a 3 px `--primary` underline and weight 600. The selected tab is reflected in the URL (`?tab=numbers`) so links and Back work.

### 4.16 Charts (Recharts)
- **Cost breakdown:** horizontal bar, sorted.
- **Means of finance:** one stacked horizontal bar (own / loan / subsidy).
- **5-year cash flow:** columns.
- **Repayment:** area of outstanding balance.
- **Comparison:** horizontal bars.

Rules for every chart: direct value labels, no pie charts, at most 5 ticks, an `aria-label` summary sentence, a "Show as table" toggle, and no entrance animation under reduced motion.

### 4.17 Banners and toasts
- **Offline banner:** `--warn-soft`, "No internet. Saved reports still open."
- **Explanation unavailable:** `--warn-soft`, "We couldn't write the explanation right now. All numbers below are complete." plus a Retry button.
- **Toasts:** bottom, above the action bar, 4 s, `aria-live="polite"`, never steal focus.

### 4.18 Empty, loading and error states
- **Loading** uses skeletons shaped like the content (VerdictCard skeleton, three metric-row skeletons), never a lone spinner for more than 1 s.
- **Empty:** an icon, one sentence, one action ("No saved reports yet" + "Build your first DPR").
- **Errors** say what happened and what to do, next to the problem, with Retry where it makes sense.

## 5. Interaction patterns

### 5.1 Intake wizard
- **Step 0 (optional, above step 1):** "Tell us in your own words" text area + mic (stretch). Submitting pre-fills the steps and shows a "We filled these from what you said, please check" banner on each pre-filled step.
- **Step 1, Where:** District → Block → Village as three searchable pickers (shadcn Command in a sheet). Each picker is enabled only after the one before it. Niphad is pre-selected for the demo.
- **Step 2, Business:** a 2 × 3 ChoiceCard grid, then a NumberStepper for unit scale with the Archetype's default.
- **Step 3, Money:** MoneyInput + chips. A helper line: "Money you can put in yourself. A bank usually expects some."
- **Step 4, About you:** only the eligibility fields the chosen Archetype needs, as ChipGroups, plus age as a NumberStepper. A helper line: "These decide which government schemes you can get."
- **Submit:** the primary button reads "Build my DPR".
- Validation runs on Next; the error appears under the field and focus moves to the first problem.
- The draft is stored in `localStorage` (wrapped in try/catch) and restored with a "Continue where you left off?" prompt.

### 5.2 Report generation
Submitting leads to the full-screen StageTrace (§4.13). It auto-opens the report 600 ms after `done`. On failure, the failed row explains what happened and offers "Try again". Engine failures are rare; LLM failures still open the report with the "explanation unavailable" banner.

### 5.3 Report page
The VerdictCard is always on top. Tabs:
- **Explanation** (default):
  - Verdict in words
  - Your village market
  - Money plan
  - Strengths and risks (SWOT shown as two simple lists, "Good" and "Watch out", with opportunities and threats inside them)
  - Pricing tips
  - How to make it work (Path to Yes, when relevant)
  - Next steps (numbered, with the document checklist)

  Plus a "Listen" button (stretch) and an "N of N numbers checked" badge with a `ShieldCheck` icon.
- **Numbers:** charts plus key MetricRows, each with Source Badges.
- **Bank DPR:** the formal document (English), plus **Share** and **Download PDF** buttons at the top.

Sticky bottom bar: **Try changes** · **Ask**.

### 5.4 What-if
**Try changes** opens a sheet.
- **Pinned strip at the top:** Scheme · Loan · EMI · Verdict icon.
- **Below it:** Own Contribution (MoneyInput + slider), Unit scale (NumberStepper + slider), Tenure (chips: 3 / 5 / 7 years).
- Each change is debounced by 250 ms and calls `/api/simulate`.
- **When the Scheme or Verdict changes:** the item pulses and a line appears: "Changed: MUDRA Kishore → Tarun".
- **Buttons:** "Reset" (ghost) and "Use these numbers" (primary). The second one re-runs the report as a new DPR, so the original stays saved.

### 5.5 Chat (Ask)
A full-height sheet with 3 suggested questions as chips ("Which documents do I need?", "What if I start smaller?", "Why not PMEGP?"). Text input with a send button, and a mic (stretch).
- Replies render figures as FigureChips and citations as Govt scheme badges linking to the source.
- A suggested change appears as a card with "Try this", which opens the what-if sheet with the values set.

### 5.6 Comparison
From the report: "Compare with another business" opens a picker of ChoiceCards (choose 1–2 more), then the result: MetricRows (Verdict, Loan, EMI, profit check, payback, market) + one bar chart + the summary paragraph. "Open full DPR" builds a report for any column.

### 5.7 Sharing and PDF
- **Share** uses `navigator.share({title, url})` when available, which opens the phone's share sheet so WhatsApp is one tap away. Otherwise it copies the link and shows a toast "Link copied".
- **Download PDF** calls `window.print()`. The print stylesheet renders the Bank DPR on A4 with the app chrome hidden.

### 5.8 Login
One screen with "Log in" / "Create account" tabs, plus a large secondary **"Continue without account"** button. Fields use `autocomplete="username"` / `current-password` / `new-password`, have a show/hide password toggle, and allow paste. After logging in, the user returns to where they came from.

## 6. Language and copy

### 6.1 Rules
- Short sentences, everyday words, second person ("you", "तुम्ही", "आप").
- **Each language is written for its speakers, not translated word for word.** A native speaker must review the `hi.json` and `mr.json` strings before the demo.
- Scheme names stay in their official form (MUDRA, PMEGP, KCC) in every language.
- **Money:**
  - headlines use lakh: "₹1.2 lakh" / "₹१.२ लाख"
  - figure sheets show the exact amount: "₹1,20,000"
  - Hindi/Marathi use Devanagari digits on the Explanation tab; the Bank DPR always uses `en-IN`
- **Time:** months and years in words: "18 months" / "१८ महिने".
- **Jargon:**

  | Term | Outside the Bank DPR tab, say |
  |---|---|
  | DSCR | "Can your profit pay the EMI?" (show "1.6×" as "profit covers EMI 1.6 times") |
  | Moratorium | "Months before EMI starts" |
  | Break-even | "Month you start making profit" |
  | Project Cost | "Total money needed" |
  | Own Contribution | "Your own money" |
  | Funding Gap | "Money to borrow" |

### 6.2 Verdict labels

| Verdict | English | हिंदी | मराठी |
|---|---|---|---|
| feasible | Good to start | शुरू करना ठीक है | सुरू करणे योग्य |
| feasible_with_changes | Possible with changes | बदलाव के साथ संभव | बदलांसह शक्य |
| not_feasible | Not advisable right now | अभी सही नहीं | सध्या योग्य नाही |

*(Pending native-speaker review.)*

### 6.3 i18n structure
- `web/src/i18n/<lang>/<namespace>.json` (one file per screen per language, merged by the loader), with flat dotted keys: `home.hero.title`, `wizard.step2.title`, `verdict.feasible`, `figure.emi`, `source.census`.
- `figure.<figure_id>` keys give the plain label for every id in `trd.md` §5.9.
- Missing keys fall back to `en`.
- The language choice persists in `localStorage` and also goes to the API as `IntakeInput.language`.

## 7. Accessibility checklist

- [ ] Body text ≥ 7:1 contrast, UI text ≥ 4.5:1, icons and borders that carry meaning ≥ 3:1
- [ ] Every input has a visible label (never placeholder-only), with errors below it linked by `aria-describedby`
- [ ] Touch targets ≥ 48 × 48 px with 8 px spacing
- [ ] Visible 3 px focus ring on every interactive element, never hidden behind sticky bars
- [ ] Verdict, better-value marks and Source Badges use icon + text, not colour alone
- [ ] Every slider has −/+ buttons
- [ ] Sheets trap focus, close on Esc, return focus to the trigger
- [ ] Route change moves focus to the page `h1`
- [ ] StageTrace, the what-if strip and toasts use polite live regions
- [ ] Charts have a summary `aria-label` and a table toggle
- [ ] `prefers-reduced-motion` respected
- [ ] Zoom never disabled; layout holds at 200% text size
- [ ] `lang` attribute on `<html>` matches the chosen language (`en`, `hi`, `mr`)

## 8. Performance on low-end phones

- Initial JS for `/` and `/new` under about 200 KB gzipped. Lazy-load Recharts and the report page (`React.lazy` per route).
- Two font weights preloaded (400, 600); the others load on demand. `font-display: swap`.
- No images on critical screens except inline SVG icons. Homepage illustrations are SVG.
- Skeletons for any wait over 300 ms. Debounce what-if at 250 ms.
- No layout shift: reserve space for the VerdictCard and charts.

## 9. Pre-delivery checklist

- [ ] Checked at 360 px, 412 px and 1280 px wide, plus 360 px landscape
- [ ] Every screen has exactly one amber button
- [ ] Every number visible to the Entrepreneur opens a FigureSheet or sits in the Bank DPR
- [ ] All three languages render without clipped or overlapping Devanagari
- [ ] Offline banner, LLM-unavailable banner, retrying stage and empty My Reports all seen at least once
- [ ] Print preview of the Bank DPR fits A4 with no app chrome
- [ ] No emoji used as icons; Lucide only
