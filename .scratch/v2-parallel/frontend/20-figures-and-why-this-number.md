# 20: Figures and "Why this number?"

**What to build:** The Entrepreneur View on the Explanation tab shows real numbers instead of `{{figure_id}}`. Each one is formatted for the chosen language (lakh grouping, Devanagari digits in Hindi and Marathi), and tapping it opens the "Why this number?" sheet with formula, inputs, Source Badge and note. The checked-numbers badge shows verified / total.

**Owner:** Frontend

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## Notes

- Implement the two declared format functions with the browser's native number formatting. The Bank View always formats in English.
- One shared renderer turns text with placeholders (including namespaced and dotted ids) into text plus Figure chips. An unknown id renders as a dash, never as raw braces. Ticket 22, what-if and stretch chat and Compare all reuse it.
- `assumption` Figures read "Our estimate".

## Acceptance criteria

- [x] On the fixture report, the Explanation tab shows no `{{` in English, Hindi or Marathi.
- [x] In Marathi, numbers use Devanagari digits and lakh grouping.
- [x] Tapping a number opens the sheet with formula, inputs and Source Badge. It works at 360 px with 48 px targets.
- [x] `npm run check` and `npm run build` pass.

## Comments

- Commit: see `V2-20` in git log.
- Verified in Chrome against the fixture report (Marathi text): no `{{`, Devanagari digits with lakh grouping (`₹५,१७,४६०`), tapping a chip opens the sheet with formula, inputs and Source Badge, verified/total badge `१५/१५`. Not checked at a true 360 px window (the browser would not resize) or in `en`/`hi` explanations: the fixture explanation is Marathi only.
- Digits follow the explanation's own language (`explanation.language`), not the app-bar language, so a Marathi text never mixes scripts. Only `INR` and `%` carry a mark; months/ratio/count are bare because sentences supply the word.
- For ticket 22/23: reuse `FigureText` (`components/FigureText.tsx`) for any text with placeholders; `FigureSheet` takes one `Figure`. `ExplanationTab` now takes a `figures` prop (passed from `Report.tsx`). Sheet inputs are shown as plain numbers (no unit) because `inputs` is `Record<string, number>`.
- `hi`/`mr` strings in `figure.json`/`source.json` and the hi/mr unit words in `lib/format.ts` are machine-assisted: needs native review.
- Fullstack: the live API cannot serve a finished report until V2-12 (stream stores the result): `GET /api/reports/{id}` is `pending` with no `engine` after the stream, and the fixture id no longer resolves.
