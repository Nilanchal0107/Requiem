# 40: Chat tool loop (stretch)

**What to build:** `chat` answers a question about a report in the chosen language. It uses read-DPR, search-schemes and simulate tools and returns a placeholder reply, extra figures, citations and suggested changes. It never changes the report.

**Owner:** AIML

**Blocked by:** None (stretch; pick up only when your core tickets are done). Search-schemes needs 43; without it, ship read-DPR and simulate only.

**Status:** done

## Acceptance criteria

- [x] In replay mode, a "what if I start with 3 animals?" question returns a suggested change and extra figures, and the reply passes `verify`.
- [x] The report passed in is unchanged after the call.

## Comments

- Commit: `V2-40: Chat tool loop` (see `git log`).
- `llm/chat.py` + `llm/prompts/chat_system.md`. Up to 3 tool rounds, then a final call with no tools. `get_dpr` returns the section with Figure values masked to `{{id}}` placeholders, so the model never reads a number. `simulate` figures are prefixed `sim.`; a later simulate replaces earlier `sim.` figures. The reply is verified against report + sim figures and failing sentences are stripped (no regeneration).
- The test mocks `complete` with a scripted tool call and runs the real engine as `what_if`; replay cache is empty (no API key).
- For Fullstack: `what_if` receives `Change`s whose `to_value` is the new value; read the new values from `to_value` and ignore `from_value` / `resulting_verdict` on input.
