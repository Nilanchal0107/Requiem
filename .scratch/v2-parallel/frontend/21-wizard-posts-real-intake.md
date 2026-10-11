# 21: Wizard posts the real intake

**What to build:** The Entrepreneur fills the 4-step wizard (Where, Business, Money, About you), and Start builds a DPR from what they entered, not the canned intake.

**Owner:** Frontend

**Blocked by:** None (can start immediately)

**Status:** done

## Notes

- **Where:** district, block and village from the localities route, with search on village, and the household count shown once a village is picked.
- **Business:** picture cards with an icon and a word, then a − / + stepper held to the Archetype's bounds, with a typical-start hint.
- **Money:** a number keypad, amount chips, and the amount in words underneath.
- **About you:** only the eligibility fields the Archetype requires, as chips, each with a one-line reason.
- Errors show next to the field. The stepper lets you go back to any earlier step.
- The draft lives in local storage and is cleared after a successful create. Delete the canned-intake file.
- Copy goes in the wizard namespace, with `hi` and `mr` machine-assisted and flagged `needs native review`.

## Acceptance criteria

- [x] Going through the demo persona at 360 px posts an intake that matches the entries, and the stage list and report follow.
- [x] Reloading mid-wizard keeps the entries.
- [x] The canned intake is gone.
- [x] `npm run check` and `npm run build` pass.

## Comments

- Commit: see `git log --grep "V2-21"`.
- Verified in Chrome at 360 px (iframe) against the fixture API: demo persona posted `village_code FX1002, dairy, 5, ₹1,00,000, female/obc/10th_pass`, the stage list ran and the report opened; reload at step 4 kept every entry; the draft is cleared on the first stage event.
- Filled in the stub components `Stepper`, `ChipGroup`, `ChoiceCard`, `MoneyInput`; `draft.ts` holds the draft, validation and intake mapping (checked in `npm run check`).
- Deferred: village/district pickers are native selects plus a village search list, not the Command sheet; no "Continue where you left off?" prompt (the draft restores silently); the stage list is still the plain text list (StageTrace is another ticket).
- `hi`/`mr` wizard copy is machine-assisted; `wizard._review` marks it `needs native review`.
- For ticket 45 (describe box): `patch()` in `NewReport` is the place to pre-fill the draft.
