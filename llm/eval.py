"""Eval: `uv run python -m llm.eval` prints scheme-match accuracy and verifier pass rate (TRD §6.7)."""
from typing import Any

from api.contracts import IntakeInput
from engine import run_engine
from llm.explain import explain_report

# Hand-labelled from the Scheme rules in data/schemes: PMEGP takes new units only, MUDRA covers the rest.
_BASE_ELIGIBILITY = {"age": 30, "gender": "female", "social_category": "obc", "education": "10th_pass"}
_PERSONAS = [
    ({**_BASE_ELIGIBILITY, "business_status": "new"}, "pmegp"),
    ({**_BASE_ELIGIBILITY, "business_status": "existing"}, "mudra"),
]
_OWN_CONTRIBUTION = {"dairy": 100000, "kirana": 50000}


def run_eval(
    cases: list[dict[str, Any]],
    *,
    archetypes: list[dict[str, Any]],
    schemes: list[dict[str, Any]],
    villages: dict[str, dict[str, Any]],
    current_year: int,
) -> dict[str, float]:
    """Run each case through the engine and the Entrepreneur View (TRD §6.7). Returns {"scheme_match": x, "verifier_pass": y}.

    A case is `{"input": IntakeInput dict, "expected_scheme": id}`. Catalogue and village rows come in as
    arguments, so eval does not import `data`. verifier_pass counts Entrepreneur Views with nothing stripped.
    """
    assert cases, "no eval cases"
    by_id = {a["id"]: a for a in archetypes}
    matched = passed = 0
    for case in cases:
        inp = IntakeInput.model_validate(case["input"])
        result = run_engine(inp, by_id[inp.archetype_id], schemes, villages[inp.village_code], current_year=current_year)
        matched += bool(result.schemes.best and result.schemes.best.scheme_id == case["expected_scheme"])
        exp = explain_report(result, inp.language)
        passed += exp.available and exp.verified == exp.total
    return {"scheme_match": matched / len(cases), "verifier_pass": passed / len(cases)}


def main() -> None:
    """Entry point for `python -m llm.eval` (TRD §6.7). Builds archetype x village x persona cases from the catalogue."""
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
                "own_contribution": _OWN_CONTRIBUTION.get(a["id"], 50000), "eligibility": elig,
            },
            "expected_scheme": expected,
        }
        for a in archetypes for code in villages for elig, expected in _PERSONAS
    ]
    assert cases, "no eval cases built"
    out = run_eval(cases, archetypes=archetypes, schemes=schemes, villages=villages, current_year=2026)
    print(f"cases: {len(cases)}")
    print(f"scheme-match accuracy: {out['scheme_match']:.0%}")
    print(f"verifier pass rate:    {out['verifier_pass']:.0%}")


if __name__ == "__main__":
    main()
