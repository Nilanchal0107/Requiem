# 44: Intake parse (stretch)

**What to build:** `parse_intake` turns a free-text idea in English, Hindi or Marathi into a partial intake. The missing fields are computed in code, not by the LLM.

**Owner:** AIML

**Blocked by:** None (stretch; pick up only when your core tickets are done). Uses the client from 05.

**Status:** done

## Acceptance criteria

- [x] In replay mode, a Marathi description of the demo dairy fills archetype and scale, and `missing_fields` lists exactly the rest.

## Comments

- Commit: `V2-44: Intake parse` (see `git log`).
- `llm/intake.py` + `llm/prompts/intake_parse.md`. Every extracted value is re-validated against the contract types; bad or unknown values are dropped, and an LLM failure returns empty `fields`. `missing` is computed by `missing_fields` (village, Archetype, scale, Own Contribution, and the four required eligibility fields).
- The test mocks `complete` (the replay cache is empty: no API key here). Record a real Marathi reply with `LLM_MODE=record` when a key is available.
