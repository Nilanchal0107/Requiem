# 44: Intake parse (stretch)

**What to build:** `parse_intake` turns a free-text idea in English, Hindi or Marathi into a partial intake. The missing fields are computed in code, not by the LLM.

**Owner:** AIML

**Blocked by:** None (stretch; pick up only when your core tickets are done). Uses the client from 05.

**Status:** ready-for-agent

## Acceptance criteria

- [ ] In replay mode, a Marathi description of the demo dairy fills archetype and scale, and `missing_fields` lists exactly the rest.
