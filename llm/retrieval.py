"""BM25 over scheme texts (TRD §6.6). Built once at startup; the corpus is English."""
from pathlib import Path

from api.contracts import Citation


class SchemeIndex:
    """Chunks `texts_dir/*.md` by `##` heading and indexes them in memory with BM25Okapi (TRD §6.6).

    `source_urls` maps scheme_id to the `source_url` from schemes.json. The caller passes it in, because
    `llm` may not import `data`.
    """

    def __init__(self, texts_dir: Path, source_urls: dict[str, str]) -> None:
        """Chunk, tokenise (lowercase `\\w+`) and index. V2 must add at least one assert check."""
        raise NotImplementedError("llm.retrieval.SchemeIndex")

    def search(self, query: str, k: int = 3) -> list[Citation]:
        """Top `k` chunks as Citation(scheme_id, source_url, snippet). The chat model translates the query first."""
        raise NotImplementedError("llm.retrieval.SchemeIndex.search")
