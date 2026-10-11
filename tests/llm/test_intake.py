"""Ticket 44: a Marathi dairy description fills archetype and scale; `missing` lists exactly the rest."""
import json
from types import SimpleNamespace

from api.contracts import IntakeParseRequest
from llm import intake
from llm.intake import missing_fields, parse_intake


def _fake(content: str):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def test_marathi_dairy_fills_archetype_and_scale_and_missing_is_the_rest(monkeypatch):
    reply = json.dumps({"archetype_id": "dairy", "unit_scale": 5, "age": 200, "gender": "robot"})
    monkeypatch.setattr(intake, "complete", lambda *a, **k: _fake(reply))
    res = parse_intake(IntakeParseRequest(text="मला ५ गायींचा दूध व्यवसाय सुरू करायचा आहे", language="mr"), ["dairy", "kirana"])
    assert res.fields == {"archetype_id": "dairy", "unit_scale": 5.0}  # bad age and gender dropped
    assert res.missing == [
        "village_code", "own_contribution",
        "eligibility.age", "eligibility.gender", "eligibility.social_category", "eligibility.education",
    ]


def test_unknown_archetype_dropped_and_llm_failure_is_empty(monkeypatch):
    monkeypatch.setattr(intake, "complete", lambda *a, **k: _fake('{"archetype_id": "spaceship"}'))
    assert "archetype_id" not in parse_intake(IntakeParseRequest(text="x"), ["dairy"]).fields

    def boom(*a, **k):
        raise FileNotFoundError("cache miss")

    monkeypatch.setattr(intake, "complete", boom)
    assert parse_intake(IntakeParseRequest(text="x"), ["dairy"]).fields == {}
    assert len(missing_fields({})) == 8
