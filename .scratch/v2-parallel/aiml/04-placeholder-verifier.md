# 04: Placeholder verifier

**What to build:** `verify(text, figures)` enforces CLAUDE.md rule 4: LLM text contains no digits, only `{{figure_id}}` placeholders that exist in the figures.

**Owner:** AIML

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## Notes

- Comparison ids are namespaced `<archetype_id>.<figure_id>` (`dairy.min_dscr`), and group ids contain dots (`cost.animals`). Both must resolve.
- The result reports verified / total and which sentences fail, so ticket 05 can strip them.

## Acceptance criteria

- [ ] Valid placeholders pass.
- [ ] An ASCII digit outside a placeholder fails.
- [ ] A Devanagari digit outside a placeholder fails.
- [ ] An unknown id fails.
- [ ] Namespaced Comparison ids and dotted group ids resolve.
- [ ] The verifier test file passes.
