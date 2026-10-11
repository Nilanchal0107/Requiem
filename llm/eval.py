"""Eval: `uv run python -m llm.eval` prints scheme-match accuracy and verifier pass rate (TRD §6.7)."""
from typing import Any

from api.contracts import IntakeInput
from engine import run_engine
from llm.explain import explain_report

_BASE_ELIGIBILITY = {"age": 30, "gender": "female", "social_category": "obc", "education": "10th_pass"}
_STATUSES = ("new", "existing")
# What each Archetype's Entrepreneur needs for its crop or trade Schemes to apply.
_ARCH_ELIGIBILITY = {"onion_cultivation": {"farmland": "owned"}, "tailoring": {"artisan_trade": True}}
_OWN_CONTRIBUTION = {
    "dairy": 100000, "kirana": 50000, "onion_cultivation": 120000,
    "poultry": 100000, "tailoring": 20000, "flour_mill": 100000,
}
# Hand-labelled from the Scheme rules in data/schemes. A list means a genuine tie: a woman gets the 35% rate under both
# PMEGP and CMEGP. CMEGP excludes dairy and poultry (negative list); only KCC covers a crop; PM Vishwakarma's 5% beats
# MUDRA for a tailor, new or existing. Everyone else: PMEGP/CMEGP for a new unit, MUDRA for an existing one.
_EXPECTED = {
    ("dairy", "new"): ["pmegp"], ("dairy", "existing"): ["mudra"],
    ("kirana", "new"): ["pmegp", "cmegp"], ("kirana", "existing"): ["mudra"],
    ("flour_mill", "new"): ["pmegp", "cmegp"], ("flour_mill", "existing"): ["mudra"],
    ("poultry", "new"): ["pmegp"], ("poultry", "existing"): ["mudra"],
    ("tailoring", "new"): ["pm_vishwakarma"], ("tailoring", "existing"): ["pm_vishwakarma"],
    ("onion_cultivation", "new"): ["kcc"], ("onion_cultivation", "existing"): ["kcc"],
}


def run_eval(
    cases: list[dict[str, Any]],
    *,
    archetypes: list[dict[str, Any]],
    schemes: list[dict[str, Any]],
    villages: dict[str, dict[str, Any]],
    current_year: int,
) -> dict[str, float]:
    """Run each case through the engine and the Entrepreneur View (TRD §6.7). Returns {"scheme_match": x, "verifier_pass": y}.

    A case is `{"input": IntakeInput dict, "expected_scheme": id or list of acceptable ids}`. Catalogue and village rows come in as
    arguments, so eval does not import `data`. verifier_pass counts Entrepreneur Views with nothing stripped.
    """
    assert cases, "no eval cases"
    by_id = {a["id"]: a for a in archetypes}
    matched = passed = 0
    for case in cases:
        inp = IntakeInput.model_validate(case["input"])
        result = run_engine(inp, by_id[inp.archetype_id], schemes, villages[inp.village_code], current_year=current_year)
        accepted = case["expected_scheme"]
        accepted = [accepted] if isinstance(accepted, str) else accepted
        matched += bool(result.schemes.best and result.schemes.best.scheme_id in accepted)
        exp = explain_report(result, inp.language)
        passed += exp.available and exp.verified == exp.total
    return {"scheme_match": matched / len(cases), "verifier_pass": passed / len(cases)}


def main() -> None:
    """Entry point for `python -m llm.eval` (TRD §6.7). Builds archetype x village x new/existing cases from the catalogue."""
    from data.loaders import load_archetypes, load_schemes  # lazy: llm never imports data at import time
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent / "data"
    osm = json.loads((root / "osm" / "niphad_counts.json").read_text(encoding="utf-8"))
    villages = {
        v["code"]: {**v, "osm_counts": osm.get(v["code"], {})}
        for v in json.loads((root / "census" / "niphad_villages.json").read_text(encoding="utf-8"))
    }
    archetypes = [a.model_dump(mode="json") for a in load_archetypes()]
    schemes = [s.model_dump(mode="json") for s in load_schemes()]
    cases = [
        {
            "input": {
                "village_code": code, "archetype_id": a["id"], "unit_scale": a["unit_scale"]["default"],
                "own_contribution": _OWN_CONTRIBUTION[a["id"]],
                "eligibility": {**_BASE_ELIGIBILITY, **_ARCH_ELIGIBILITY.get(a["id"], {}), "business_status": status},
            },
            "expected_scheme": _EXPECTED[(a["id"], status)],  # KeyError = a new Archetype still needs its labels
        }
        for a in archetypes for code in villages for status in _STATUSES
    ]
    assert cases, "no eval cases built"
    out = run_eval(cases, archetypes=archetypes, schemes=schemes, villages=villages, current_year=2026)
    print(f"cases: {len(cases)}")
    print(f"scheme-match accuracy: {out['scheme_match']:.0%}")
    print(f"verifier pass rate:    {out['verifier_pass']:.0%}")


if __name__ == "__main__":
    main()
