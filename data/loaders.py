"""Loaders for the catalogue folders and the village seed (TRD §4.3, §4.4). Declared in ticket 08; bodies arrive in V2."""
from sqlmodel import Session

from data.models import Archetype, Scheme


def load_archetypes() -> list[Archetype]:
    """Reads every data/archetypes/<id>.json and validates each against Archetype."""
    raise NotImplementedError("data.loaders.load_archetypes")


def load_schemes() -> list[Scheme]:
    """Reads every data/schemes/<id>.json and validates each against Scheme."""
    raise NotImplementedError("data.loaders.load_schemes")


def load_scheme_texts() -> dict[str, str]:
    """Reads data/scheme_texts/<scheme_id>.md. Returns scheme_id -> markdown, for BM25 retrieval (llm.retrieval)."""
    raise NotImplementedError("data.loaders.load_scheme_texts")


def seed_villages(session: Session) -> int:
    """Reads data/census/ and data/osm/niphad_counts.json, then upserts into the `village` table. Idempotent. Returns rows written."""
    raise NotImplementedError("data.loaders.seed_villages")
