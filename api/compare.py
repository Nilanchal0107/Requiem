from fastapi import APIRouter, HTTPException

from api.contracts import CompareRequest, Comparison, EngineResult
from api.settings import fixture

router = APIRouter(prefix="/api", tags=["compare"])


# shortcut: canned summary text in English whatever the language; V2 swaps in the LLM summary
@router.post("/compare", response_model=Comparison)
def compare(body: CompareRequest):
    archetypes = {a["id"]: a for a in fixture("archetypes.json")}
    unknown = [aid for aid in body.archetype_ids if aid not in archetypes]
    if unknown:
        raise HTTPException(400, f"unknown archetype: {unknown[0]}")
    base = fixture("report.json")["engine"]
    results = [EngineResult.model_validate({**base, "archetype_id": aid}) for aid in body.archetype_ids]
    summary = " ".join(
        f"{archetypes[aid]['name']} has a minimum DSCR of {{{{{aid}.min_dscr}}}} "
        f"and a funding gap of {{{{{aid}.funding_gap}}}}."
        for aid in body.archetype_ids
    )
    return Comparison(results=results, summary=summary, language=body.input.language)
