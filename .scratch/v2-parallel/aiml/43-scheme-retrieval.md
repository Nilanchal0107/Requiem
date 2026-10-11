# 43: Scheme retrieval (stretch)

**What to build:** BM25 search over the saved scheme text returns the top passages as `Citation`s carrying each Scheme's source URL. No embeddings.

**Owner:** AIML

**Blocked by:** None (stretch; pick up only when your core tickets are done). Needs the scheme text from 01.

**Status:** done

## Acceptance criteria

- [x] A query naming a PMEGP term returns a PMEGP citation first, with its source URL.

## Comments

- Commit: `V2-43: Scheme retrieval` (see `git log`).
- `llm/retrieval.py`: chunks `data/scheme_texts/*.md` by `##` heading, BM25Okapi over the chunk plus its scheme id. Zero-score chunks and empty queries return nothing.
- `tests/llm/test_retrieval.py`: a PMEGP query ranks PMEGP first with its `source_url`.
