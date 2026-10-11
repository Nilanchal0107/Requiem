"""Live competitor counts from OpenStreetMap Overpass (TRD §4.4). The network call lives here, never in engine/.

Falls back silently (returns {}) so the caller keeps the seeded counts from data/osm/niphad_counts.json.
"""
import json
import logging
import os
import tempfile
import time
from pathlib import Path
import urllib.request
from urllib.parse import urlencode

log = logging.getLogger(__name__)

OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
OSM_LIVE = os.getenv("OSM_LIVE", "0").lower() not in ("0", "false", "no", "off")
RADIUS_M = 3000   # ponytail: one reach radius for every archetype; move to Market in data/models.py if they differ
BBOX = "19.5,73.3,20.6,74.8"  # ponytail: Nashik district only (demo scope); the district-area lookup it replaces timed out on public Overpass
OSM_FILE = Path(__file__).parent / "osm" / "niphad_counts.json"
TTL_S = 24 * 3600
TIMEOUT_S = 10
_HEADERS = {"User-Agent": "requiem-hackathon/0.1", "Accept": "*/*"}  # Overpass answers 406 without these

_cache: dict[tuple[str, str], tuple[float, int]] = {}  # ponytail: per-process; persist in the DB if restarts matter


def _q(s: str) -> str:
    """Quotes a value for Overpass QL."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_query(village_name: str, tags: list[str], radius_m: int = RADIUS_M) -> str:
    """Overpass QL: finds the village's place node inside BBOX, then counts tagged features around it."""
    around = "".join(
        f"nwr(around.v:{radius_m})[{_q(k)}={_q(v)}];" for k, v in (t.split("=", 1) for t in tags)
    )
    return (
        "[out:json][timeout:25];"
        f'node["place"]["name"={_q(village_name)}]({BBOX})->.v;'
        f"({around})->.c;"
        ".v out count;.c out count;"
    )


def parse_counts(payload: dict) -> int | None:
    """Reads the two `count` elements: village found, competitors. None when the village node was not found."""
    totals = [int(e["tags"]["total"]) for e in payload["elements"] if e["type"] == "count"]
    assert len(totals) == 2, f"expected 2 count elements, got {len(totals)}"
    return totals[1] if totals[0] > 0 else None


def save_counts(village_code: str, counts: dict[str, int], path: Path = OSM_FILE) -> None:
    """Writes live counts into the committed snapshot, so the next run (or an offline demo) reads them. Atomic replace."""
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data[village_code] = {**data.get(village_code, {}), **counts}
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)  # ponytail: read-modify-write, fine for one localhost process; lock if several workers


def fetch_count(village_name: str, tags: list[str]) -> int | None:
    """One Overpass call. None on any failure or when the village is not in OSM."""
    body = urlencode({"data": build_query(village_name, tags)}).encode()
    try:
        req = urllib.request.Request(OVERPASS_URL, data=body, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            return parse_counts(json.load(resp))
    except Exception as exc:  # network, HTTP, JSON: all mean "use the seeded counts"
        log.warning("Overpass failed for %s: %s", village_name, exc)
        return None


def live_osm_counts(village: dict, archetype: dict) -> dict[str, int]:
    """{archetype_id: count} fetched now, or {} (live off, no OSM tags, village not found, call failed)."""
    tags = archetype.get("market", {}).get("competitor_osm_tags", [])
    if not OSM_LIVE or not tags:
        return {}
    key = (village["code"], archetype["id"])
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < TTL_S:
        return {archetype["id"]: hit[1]}
    count = fetch_count(village["name"], tags)
    if count is None:
        return {}
    _cache[key] = (time.time(), count)
    save_counts(village["code"], {archetype["id"]: count})
    return {archetype["id"]: count}


if __name__ == "__main__":
    q = build_query('Lasa"galaon', ["shop=convenience", "shop=grocery"])
    assert '\\"' in q and q.count("nwr(around.v:3000)") == 2, q
    assert parse_counts({"elements": [{"type": "count", "tags": {"total": "1"}}, {"type": "count", "tags": {"total": "7"}}]}) == 7
    assert parse_counts({"elements": [{"type": "count", "tags": {"total": "0"}}, {"type": "count", "tags": {"total": "0"}}]}) is None
    import json as _j, pathlib, tempfile as _t
    f = pathlib.Path(_t.mkdtemp()) / "c.json"
    f.write_text('{"a": {"kirana": 12}}')
    save_counts("a", {"dairy": 1}, f)
    save_counts("b", {"kirana": 0}, f)
    assert _j.loads(f.read_text()) == {"a": {"kirana": 12, "dairy": 1}, "b": {"kirana": 0}}
    assert live_osm_counts({"code": "x", "name": "x"}, {"id": "dairy", "market": {"competitor_osm_tags": []}}) == {}
    print("osm_live ok")
