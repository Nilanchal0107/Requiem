# 21: Wizard posts the real intake

**What to build:** The Entrepreneur fills the 4-step wizard (Where, Business, Money, About you), and Start builds a DPR from what they entered, not the canned intake.

**Owner:** Frontend

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## Notes

- **Where:** district, block and village from the localities route, with search on village, and the household count shown once a village is picked.
- **Business:** picture cards with an icon and a word, then a − / + stepper held to the Archetype's bounds, with a typical-start hint.
- **Money:** a number keypad, amount chips, and the amount in words underneath.
- **About you:** only the eligibility fields the Archetype requires, as chips, each with a one-line reason.
- Errors show next to the field. The stepper lets you go back to any earlier step.
- The draft lives in local storage and is cleared after a successful create. Delete the canned-intake file.
- Copy goes in the wizard namespace, with `hi` and `mr` machine-assisted and flagged `needs native review`.

## Acceptance criteria

- [ ] Going through the demo persona at 360 px posts an intake that matches the entries, and the stage list and report follow.
- [ ] Reloading mid-wizard keeps the entries.
- [ ] The canned intake is gone.
- [ ] `npm run check` and `npm run build` pass.
