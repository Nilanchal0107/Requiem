"""Saves a text snapshot of each Scheme's official page to data/scheme_sources/<id>.txt and prints what changed.

    python -m data.refresh_scheme_sources [scheme_id ...]

A person reviews the diff, then edits data/schemes/<id>.json (rules, verified_on) and data/scheme_texts/<id>.md by hand
(CLAUDE.md rule 6). A failed or near-empty fetch leaves the old snapshot untouched and exits 1.
"""
import difflib
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from data.loaders import load_schemes

OUT = Path(__file__).parent / "scheme_sources"
MIN_CHARS = 200  # shorter than this is an error page or a JS shell, not a policy page
_SKIP = {"script", "style", "noscript", "head"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        self._depth += tag in _SKIP

    def handle_endtag(self, tag):
        self._depth -= tag in _SKIP and self._depth > 0

    def handle_data(self, data):
        if not self._depth and data.strip():
            self.parts.append(" ".join(data.split()))


def html_to_text(html: str) -> str:
    p = _Text()
    p.feed(html)
    return "\n".join(p.parts)


def snapshot(url: str, fetched_on: str, text: str) -> str:
    return f"source_url: {url}\nfetched_on: {fetched_on}\n\n{text}\n"


def body(snap: str) -> str:
    return snap.split("\n\n", 1)[1] if "\n\n" in snap else snap


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "requiem-hackathon/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # TLS verification stays on
        text = html_to_text(resp.read().decode(resp.headers.get_content_charset() or "utf-8", errors="replace"))
    if len(text) < MIN_CHARS:
        raise ValueError(f"only {len(text)} characters of text; error page or JavaScript-rendered?")
    return text


def main(ids: list[str]) -> int:
    failed = 0
    OUT.mkdir(exist_ok=True)
    for s in load_schemes():
        if ids and s.id not in ids:
            continue
        path = OUT / f"{s.id}.txt"
        try:
            new = snapshot(s.source_url, date.today().isoformat(), fetch_text(s.source_url))
        except Exception as exc:
            print(f"FAILED {s.id}: {exc}; kept the old snapshot")
            failed += 1
            continue
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if body(old) == body(new):
            print(f"unchanged {s.id}")
            continue
        diff = "".join(difflib.unified_diff(body(old).splitlines(True), body(new).splitlines(True), "saved", "fetched"))
        path.write_text(new, encoding="utf-8")
        print(f"CHANGED {s.id} (review, then update data/schemes/{s.id}.json by hand):\n{diff[:3000]}")
    return 1 if failed else 0


if __name__ == "__main__":
    assert html_to_text("<head><title>x</title></head><script>var a=1</script><p>Hello  <b>world</b></p>") == "Hello\nworld"
    assert body(snapshot("u", "2026-01-01", "text")) == "text\n"
    try:
        fetch_text("http://127.0.0.1:9/")
        raise SystemExit("expected failure")
    except OSError:
        pass
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    print("refresh_scheme_sources ok")
