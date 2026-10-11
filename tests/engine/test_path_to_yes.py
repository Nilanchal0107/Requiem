"""Ticket 06: Path to Yes returns changes that really reach feasible, inside the bounds."""
import json
from pathlib import Path

from api.contracts import IntakeInput
from engine import run_engine

ROOT = Path(__file__).resolve().parents[2]


def _load(rel):
    return json.loads((ROOT / rel).read_text())


def _setup():
    archetypes = {a: _load(f"data/archetypes/{a}.json") for a in ("dairy", "kirana")}
    schemes = [_load(f"data/schemes/{s}.json") for s in ("mudra", "pmegp", "standup_india")]
    osm = _load("data/osm/niphad_counts.json")
    villages = [{**v, "osm_counts": osm.get(v["code"], {})} for v in _load("data/census/niphad_villages.json")]
    return archetypes, schemes, villages


ELIG = {"age": 30, "gender": "female", "social_category": "obc", "education": "10th_pass",
        "business_status": "new", "prior_subsidy": False, "prior_tarun_repaid": False,
        "artisan_trade": False, "farmland": "none"}


def test_path_to_yes_changes_reach_feasible_within_bounds():
    archetypes, schemes, villages = _setup()
    found = 0
    for v in villages:
        for arch in archetypes.values():
            sc = arch["unit_scale"]
            for scale in (sc["default"], sc["max"]):
                for own in (0, 20000, 100000):
                    inp = IntakeInput(village_code=v["code"], archetype_id=arch["id"], unit_scale=scale,
                                      own_contribution=own, eligibility=ELIG)
                    res = run_engine(inp, arch, schemes, v, current_year=2026)
                    if res.verdict.level == "feasible":
                        assert res.path_to_yes is None
                        continue
                    assert res.path_to_yes is not None
                    best = res.schemes.best
                    max_tenure = next((s["max_tenure_months"] for s in schemes if best and s["id"] == best.scheme_id), None)
                    for c in res.path_to_yes.changes:
                        found += 1
                        again = run_engine(inp.model_copy(update={c.field: c.to_value}), arch, schemes, v,
                                           current_year=2026, with_path_to_yes=False)
                        assert again.verdict.level == "feasible"
                        if c.field == "unit_scale":
                            assert sc["min"] <= c.to_value <= sc["max"]
                        if c.field == "tenure_months":
                            assert c.to_value <= max_tenure
    assert found > 0, "no non-feasible case produced a suggestion; widen the grid"
