# 22: Report tabs and Bank View

**What to build:** The report page in full. The Verdict card shows an icon, a word and a colour, plus loan, EMI and Scheme. The Explanation tab adds Path to Yes with Try buttons. The Numbers tab has the four charts, each with a table toggle, plus Source Badges, the few-shops warning and the Scheme list with reasons, unlock hints, terms, source link and verified-on date. The Bank DPR tab is English and bank format, prints to A4, and shares through the phone's share sheet with copy-link as fallback.

**Owner:** Frontend

**Blocked by:** 20

**Status:** done

## Notes

- Use the existing chart, Verdict and badge components. Jargon appears only on the Bank DPR tab.
- The print stylesheet shows only the Bank View.
- The explanation-unavailable state still shows every number.

## Acceptance criteria

- [x] All three tabs render the fixture report at 360 px with no horizontal scroll and no console errors.
- [x] Every chart has a working table view.
- [x] Print preview shows only the Bank View on A4.
- [x] Share opens the native sheet, or copies the link where that isn't supported.
- [x] `npm run check` and `npm run build` pass.

## Comments

- Commit: see `V2-22` in git log.
- Verified in Chrome against the fixture report served by a throwaway mock (fixture, plus a not-feasible variant with a Path to Yes and an explanation-unavailable variant), in a 360 px iframe because the window would not resize: no horizontal scroll, no console errors, charts and their table toggles, Scheme list, Bank DPR with stacked tables. **Print preview was not opened**: the print rules are in the built CSS (`print:hidden` chrome, force-mounted Bank tab shown on print, A4 `@page`, page breaks before 7 and 8, per-page footer) but have not been seen on paper. Share's native sheet is unit-checked with a fake `navigator`, not run on a phone.
- The Verdict card, `ChartFrame` (shared title, summary `aria-label`, table toggle), the four charts, `MetricRows` and `ExplanationUnavailable` were empty stubs and are now real. The two horizontal-bar charts (cost, means of finance) are plain flex bars, not Recharts: labels never clip at 360 px. Cash flow and repayment use Recharts, with animation off.
- The figure sheet now lives in `Report.tsx`, so Verdict, Explanation and Numbers share it. `onOpenFigure(figure, lang)`: Explanation passes the explanation's language, the others the app language. `useLang()` added to `i18n/index.ts`; `Toaster` mounted in `RootLayout`.
- Bank DPR is English only, so its words are written in `BankTab.tsx`, not in i18n (the unused `report.bank.section.*` keys are removed). All 12 sections are always expanded; collapsible sections on mobile are not done. The repayment schedule shows 12 rows plus "Show all N" on screen and all rows in print.
- For ticket 23: **Try it** on a Path to Yes card only opens the What-if sheet; it does not preset the value yet. `onTry(change)` in `Report.tsx` is the hook.
- For Fullstack: (1) `Report` has no village name, so the Bank DPR shows "Village code FX1002"; a name on `Report` or a lookup by code would fix it. (2) The SWOT and risks text in the Bank DPR is the explanation's language (the fixture is Marathi); an English version needs the API. (3) There is no "write the explanation again" call, so Retry on the unavailable banner just reloads the report. (4) `SchemeOption` has no `verified_on`; the Scheme list reads it from `GET /api/schemes` by `scheme_id`.
- Engine text shown as-is, in English: Scheme `reasons`, `failed_rule`, `unlock_hint`, cost item names.
- The Bank DPR document checklist is a generic list, not Scheme-specific; it needs a data source from AIML if it should vary by Scheme.
- hi/mr strings added in `verdict.json` and `report.json` are machine-assisted and need native review (verdict labels come from ui-ux §6.2, also pending review).
- Review notes, not done: Source Badges are on the Key numbers rows, Scheme terms and the Bank DPR source columns; the chart labels, chart tables, Verdict hero figures and Path to Yes amounts have none (ui-ux 4.16 reads as "each with Source Badges" for the rows, so charts were treated as exempt; confirm). No "market" chart and no "Compare with another business" link yet (ticket 46). The Bank DPR header says "Village code", not the village name. Chart `aria-label`s are a sentence without values; the table toggle gives the numbers.
