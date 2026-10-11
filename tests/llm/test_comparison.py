"""Ticket 42: the comparison summary passes verify against the merged, namespaced figures of 2 results."""
import json
from pathlib import Path
from types import SimpleNamespace

from api.contracts import IntakeInput
from engine import run_engine
from llm import explain
from llm.verifier import verify

ROOT = Path(__file__).resolve().parents[2]


def _load(rel):
    return json.loads((ROOT / rel).read_text())


def test_comparison_summary_verifies_against_namespaced_figures(monkeypatch):
    schemes = [_load(f"data/schemes/{s}.json") for s in ("mudra", "pmegp", "standup_india")]
    village = {**_load("data/census/niphad_villages.json")[0], "osm_counts": {}}
    elig = {"age": 30, "gender": "female", "social_category": "obc", "education": "10th_pass"}
    results = []
    for aid, own in (("dairy", 100000), ("kirana", 50000)):
        arch = _load(f"data/archetypes/{aid}.json")
        inp = IntakeInput(village_code=village["code"], archetype_id=aid, unit_scale=arch["unit_scale"]["default"],
                          own_contribution=own, eligibility=elig)
        results.append(run_engine(inp, arch, schemes, village, current_year=2026))

    text = "Dairy keeps repayment cover {{dairy.min_dscr}}. Kirana has only {{kirana.min_dscr}}. It costs 5 lakh."
    fake = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])
    monkeypatch.setattr(explain, "complete", lambda *a, **k: fake)

    summary = explain.explain_comparison(results, "en")
    merged = {f"{r.archetype_id}.{k}": f for r in results for k, f in r.figures.items()}
    assert "{{dairy.min_dscr}}" in summary and "lakh" not in summary  # digit sentence stripped
    assert verify(summary, merged).offending == []
