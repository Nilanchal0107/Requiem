# 22: Report tabs and Bank View

**What to build:** The report page in full. The Verdict card shows an icon, a word and a colour, plus loan, EMI and Scheme. The Explanation tab adds Path to Yes with Try buttons. The Numbers tab has the four charts, each with a table toggle, plus Source Badges, the few-shops warning and the Scheme list with reasons, unlock hints, terms, source link and verified-on date. The Bank DPR tab is English and bank format, prints to A4, and shares through the phone's share sheet with copy-link as fallback.

**Owner:** Frontend

**Blocked by:** 20

**Status:** ready-for-agent

## Notes

- Use the existing chart, Verdict and badge components. Jargon appears only on the Bank DPR tab.
- The print stylesheet shows only the Bank View.
- The explanation-unavailable state still shows every number.

## Acceptance criteria

- [ ] All three tabs render the fixture report at 360 px with no horizontal scroll and no console errors.
- [ ] Every chart has a working table view.
- [ ] Print preview shows only the Bank View on A4.
- [ ] Share opens the native sheet, or copies the link where that isn't supported.
- [ ] `npm run check` and `npm run build` pass.
