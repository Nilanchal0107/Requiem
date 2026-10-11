"""BM25 over scheme texts (TRD §6.6). Built once at startup; the corpus is English."""
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from api.contracts import Citation

_TOKEN_RE = re.compile(r"\w+")


def _tokenise(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class SchemeIndex:
    """Chunks `texts_dir/*.md` by `##` heading and indexes them in memory with BM25Okapi (TRD §6.6).

    `source_urls` maps scheme_id to the `source_url` from schemes.json. The caller passes it in, because
    `llm` may not import `data`.
    """

    def __init__(self, texts_dir: Path, source_urls: dict[str, str]) -> None:
        """Chunk, tokenise (lowercase word characters) and index."""
        self._chunks: list[tuple[str, str]] = []  # (scheme_id, chunk text)
        for path in sorted(Path(texts_dir).glob("*.md")):
            # the part before the first "## " is the title block, which is no passage
            for part in re.split(r"^## ", path.read_text(encoding="utf-8"), flags=re.M)[1:]:
                self._chunks.append((path.stem, "## " + part.strip()))
        assert self._chunks, f"no scheme text chunks found in {texts_dir}"
        self._source_urls = source_urls
        # title included in the indexed text so "PMEGP" matches every chunk of its own scheme
        self._bm25 = BM25Okapi([_tokenise(f"{sid} {text}") for sid, text in self._chunks])

    def search(self, query: str, k: int = 3) -> list[Citation]:
        """Top `k` chunks as Citation(scheme_id, source_url, snippet). The chat model translates the query first."""
        tokens = _tokenise(query)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)
        top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [
            Citation(scheme_id=self._chunks[i][0], source_url=self._source_urls.get(self._chunks[i][0], ""),
                     snippet=self._chunks[i][1])
            for i in top
            if scores[i] > 0
        ]
