# 40: Chat tool loop (stretch)

**What to build:** `chat` answers a question about a report in the chosen language. It uses read-DPR, search-schemes and simulate tools and returns a placeholder reply, extra figures, citations and suggested changes. It never changes the report.

**Owner:** AIML

**Blocked by:** None (stretch; pick up only when your core tickets are done). Search-schemes needs 43; without it, ship read-DPR and simulate only.

**Status:** ready-for-agent

## Acceptance criteria

- [ ] In replay mode, a "what if I start with 3 animals?" question returns a suggested change and extra figures, and the reply passes `verify`.
- [ ] The report passed in is unchanged after the call.
