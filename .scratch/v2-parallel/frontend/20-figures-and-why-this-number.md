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

- [ ] On the fixture report, the Explanation tab shows no `{{` in English, Hindi or Marathi.
- [ ] In Marathi, numbers use Devanagari digits and lakh grouping.
- [ ] Tapping a number opens the sheet with formula, inputs and Source Badge. It works at 360 px with 48 px targets.
- [ ] `npm run check` and `npm run build` pass.
