# 04: Placeholder verifier

**What to build:** `verify(text, figures)` enforces CLAUDE.md rule 4: LLM text contains no digits, only `{{figure_id}}` placeholders that exist in the figures.

**Owner:** AIML

**Blocked by:** None (can start immediately)

**Status:** done

## Notes

- Comparison ids are namespaced `<archetype_id>.<figure_id>` (`dairy.min_dscr`), and group ids contain dots (`cost.animals`). Both must resolve.
- The result reports verified / total and which sentences fail, so ticket 05 can strip them.

## Acceptance criteria

- [x] Valid placeholders pass.
- [x] An ASCII digit outside a placeholder fails.
- [x] A Devanagari digit outside a placeholder fails.
- [x] An unknown id fails.
- [x] Namespaced Comparison ids and dotted group ids resolve.
- [x] The verifier test file passes.

## Comments

- Implemented `verify(text, figures)` in `llm/verifier.py` with `_split_sentences` masking placeholders so internal dots (`dairy.min_dscr`) do not cause spurious sentence splits.
- Checked placeholders against `figures` and scanned residual text for ASCII (`[0-9]`) and Devanagari (`[०-९]`) digits.
- Unskipped and expanded `tests/test_verifier.py` to cover valid placeholders, ASCII digits, Devanagari digits, unknown IDs, namespaced Comparison IDs, dotted group IDs, and multi-sentence texts.
- All 7 tests in `tests/test_verifier.py` pass.

