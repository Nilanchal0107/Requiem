"""Ticket 43: a query naming a PMEGP term returns a PMEGP citation first, with its source URL."""
import json
from pathlib import Path

from llm.retrieval import SchemeIndex

ROOT = Path(__file__).resolve().parents[2]


def _index() -> SchemeIndex:
    urls = {p.stem: json.loads(p.read_text())["source_url"] for p in (ROOT / "data" / "schemes").glob("*.json")}
    return SchemeIndex(ROOT / "data" / "scheme_texts", urls)


def test_pmegp_query_ranks_pmegp_first_with_source_url():
    hits = _index().search("PMEGP back-ended subsidy lock-in period")
    assert hits and hits[0].scheme_id == "pmegp"
    assert hits[0].source_url == "https://www.kviconline.gov.in/pmegpeportal/"
    assert _index().search("") == []
