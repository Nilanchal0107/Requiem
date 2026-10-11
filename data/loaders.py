"""Loaders for the catalogue folders and the village seed (TRD §4.3, §4.4). Declared in ticket 08; bodies arrive in V2."""
import json
from pathlib import Path

from sqlmodel import Session

from data.models import Archetype, Scheme

_DATA = Path(__file__).parent


def load_archetypes() -> list[Archetype]:
    """Reads every data/archetypes/<id>.json and validates each against Archetype.

    Raises ValidationError if any file is malformed (extra keys, wrong types, missing fields).
    """
    folder = _DATA / "archetypes"
    files = sorted(folder.glob("*.json"))
    assert files, f"No archetype JSON files found in {folder}"
    return [Archetype.model_validate(json.loads(p.read_text())) for p in files]


def load_schemes() -> list[Scheme]:
    """Reads every data/schemes/<id>.json and validates each against Scheme.

    Raises ValidationError if any file is malformed. source_url and verified_on are required (CLAUDE.md rule 6).
    """
    folder = _DATA / "schemes"
    files = sorted(folder.glob("*.json"))
    assert files, f"No scheme JSON files found in {folder}"
    return [Scheme.model_validate(json.loads(p.read_text())) for p in files]


def load_scheme_texts() -> dict[str, str]:
    """Reads data/scheme_texts/<scheme_id>.md. Returns scheme_id -> markdown, for BM25 retrieval (llm.retrieval)."""
    folder = _DATA / "scheme_texts"
    texts: dict[str, str] = {}
    for p in sorted(folder.glob("*.md")):
        texts[p.stem] = p.read_text()
    assert texts, f"No scheme text .md files found in {folder}"
    return texts


def seed_villages(session: Session) -> int:
    """Reads data/census/ and data/osm/niphad_counts.json, then upserts into the `village` table. Idempotent. Returns rows written."""
    from api.db import Village  # imported here so data/ never imports api/ at module level

    census_folder = _DATA / "census"
    osm_file = _DATA / "osm" / "niphad_counts.json"

    villages_raw: list[dict] = []
    for p in sorted(census_folder.glob("*.json")):
        data = json.loads(p.read_text())
        assert isinstance(data, list), f"{p} must be a JSON array"
        villages_raw.extend(data)

    assert villages_raw, f"No village records found in {census_folder}"

    osm_counts: dict[str, dict[str, int]] = {}
    if osm_file.exists():
        osm_counts = json.loads(osm_file.read_text())

    written = 0
    for row in villages_raw:
        code = row["code"]
        existing = session.get(Village, code)
        v = Village(
            code=code,
            name=row["name"],
            block_code=row["block_code"],
            block_name=row["block_name"],
            district_code=row["district_code"],
            district_name=row["district_name"],
            households=row["households"],
            population=row["population"],
            literacy_rate=row.get("literacy_rate", 0.0),
            workers=row.get("workers", 0),
            is_rural=row.get("is_rural", True),
            osm_counts=osm_counts.get(code, {}),
        )
        if existing:
            for k, val in v.model_dump().items():
                setattr(existing, k, val)
            session.add(existing)
        else:
            session.add(v)
        written += 1

    session.commit()
    return written
