"""Tests for Ticket 01: catalogue loaders and village seed (data/tests/)."""
import pytest

from data.loaders import load_archetypes, load_scheme_texts, load_schemes


def test_load_archetypes_returns_expected_ids():
    archetypes = load_archetypes()
    ids = {a.id for a in archetypes}
    assert "dairy" in ids, "dairy archetype missing"
    assert "kirana" in ids, "kirana archetype missing"


def test_load_archetypes_count():
    archetypes = load_archetypes()
    assert len(archetypes) == 2, f"Expected 2 archetypes, got {len(archetypes)}"


def test_load_archetypes_validated_model():
    """Validates that models parse correctly (extra keys raise ValidationError)."""
    archetypes = load_archetypes()
    for a in archetypes:
        assert a.id
        assert a.name
        assert a.unit_scale.min < a.unit_scale.max
        assert a.cost_items, f"{a.id}: no cost items"


def test_load_schemes_returns_expected_ids():
    schemes = load_schemes()
    ids = {s.id for s in schemes}
    assert "mudra" in ids, "mudra scheme missing"
    assert "pmegp" in ids, "pmegp scheme missing"
    assert "standup_india" in ids, "standup_india scheme missing"


def test_load_schemes_count():
    schemes = load_schemes()
    assert len(schemes) == 3, f"Expected 3 schemes, got {len(schemes)}"


def test_every_scheme_rule_has_source_url_and_verified_on():
    """ADR 0001 / CLAUDE.md rule 6: every Scheme is traceable."""
    schemes = load_schemes()
    for s in schemes:
        assert s.source_url, f"{s.id}: missing source_url"
        assert s.verified_on, f"{s.id}: missing verified_on"


def test_scheme_texts_loader():
    texts = load_scheme_texts()
    assert "mudra" in texts, "mudra scheme text missing"
    assert "pmegp" in texts, "pmegp scheme text missing"
    assert "standup_india" in texts, "standup_india scheme text missing"
    for scheme_id, text in texts.items():
        assert len(text) > 50, f"{scheme_id}: scheme text is too short"


def test_malformed_file_raises(tmp_path, monkeypatch):
    """A malformed JSON file must raise, never silently skip."""
    import json

    # Write a bad archetype (missing required fields)
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps({"id": "bad", "name": "Bad", "extra_unknown_field": True}))

    from data import loaders

    original = loaders._DATA
    # Monkeypatch the archetypes folder to point to our tmp dir
    monkeypatch.setattr(loaders, "_DATA", tmp_path)
    (tmp_path / "archetypes").mkdir()
    (tmp_path / "archetypes" / "bad.json").write_text(
        json.dumps({"id": "bad", "unknown_key": True})
    )

    with pytest.raises(Exception):
        load_archetypes()


def test_seed_villages_inserts_three_villages():
    from sqlmodel import create_engine, Session, SQLModel
    from api.db import Village
    from data.loaders import seed_villages

    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        count = seed_villages(session)
        assert count == 3
        villages = session.query(Village).all()
        assert len(villages) == 3
        names = {v.name for v in villages}
        assert "Lasalgaon" in names

