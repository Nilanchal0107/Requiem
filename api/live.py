"""Shared loaders for the real engine and LLM routes (V3). One place that turns data/ + DB rows into engine inputs."""
from datetime import date
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from sqlmodel import Session

from api import db
from api.contracts import Change, EngineResult, IntakeInput
from data.loaders import load_archetypes, load_schemes
from engine import run_engine
from llm.retrieval import SchemeIndex

_ROOT = Path(__file__).resolve().parent.parent


@lru_cache
def archetypes() -> dict[str, dict]:
    return {a.id: a.model_dump(mode="json") for a in load_archetypes()}


@lru_cache
def schemes() -> list[dict]:
    return [s.model_dump(mode="json") for s in load_schemes()]


@lru_cache
def scheme_index() -> SchemeIndex:
    return SchemeIndex(_ROOT / "data" / "scheme_texts", {s["id"]: s["source_url"] for s in schemes()})


def village(session: Session, code: str) -> dict:
    row = session.get(db.Village, code)
    if row is None:
        raise HTTPException(400, f"unknown village: {code}")
    return row.model_dump()


def engine_for(intake: IntakeInput, session: Session, *, with_path_to_yes: bool = True) -> EngineResult:
    arch = archetypes().get(intake.archetype_id)
    if arch is None:
        raise HTTPException(400, f"unknown archetype: {intake.archetype_id}")
    return run_engine(intake, arch, schemes(), village(session, intake.village_code),
                      current_year=date.today().year, with_path_to_yes=with_path_to_yes)


def apply_changes(intake: IntakeInput, changes: list[Change]) -> IntakeInput:
    return intake.model_copy(update={c.field: (int(c.to_value) if c.field != "unit_scale" else c.to_value) for c in changes})
