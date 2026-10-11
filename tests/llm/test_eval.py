"""Ticket 48 (eval half): run_eval reports scheme-match accuracy and verifier pass rate."""
import json
from pathlib import Path

from api.contracts import Explanation, Swot
from llm import eval as ev

ROOT = Path(__file__).resolve().parents[2]


def _load(rel):
    return json.loads((ROOT / rel).read_text())


def test_run_eval_scores_scheme_match_and_verifier_pass(monkeypatch):
    def fake_explain(result, language):
        return Explanation(language=language, sections=[], swot=Swot(strengths=[], weaknesses=[], opportunities=[], threats=[]),
                           verified=3, total=3, regenerated=False, available=True)

    monkeypatch.setattr(ev, "explain_report", fake_explain)
    arch = _load("data/archetypes/dairy.json")
    schemes = [_load(f"data/schemes/{s}.json") for s in ("mudra", "pmegp", "standup_india")]
    village = _load("data/census/niphad_villages.json")[0]
    elig = {"age": 30, "gender": "female", "social_category": "obc", "education": "10th_pass", "business_status": "new"}
    inp = {"village_code": village["code"], "archetype_id": "dairy", "unit_scale": 5, "own_contribution": 100000, "eligibility": elig}
    cases = [{"input": inp, "expected_scheme": "pmegp"}, {"input": inp, "expected_scheme": "mudra"}]
    out = ev.run_eval(cases, archetypes=[arch], schemes=schemes, villages={village["code"]: {**village, "osm_counts": {}}}, current_year=2026)
    assert out == {"scheme_match": 0.5, "verifier_pass": 1.0}
