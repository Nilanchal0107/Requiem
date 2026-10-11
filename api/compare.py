from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from api import live
from api.contracts import CompareRequest, Comparison
from api.deps import get_session
from llm.explain import explain_comparison

router = APIRouter(prefix="/api", tags=["compare"])


@router.post("/compare", response_model=Comparison)
def compare(body: CompareRequest, session: Session = Depends(get_session)):
    archetypes = live.archetypes()
    unknown = [aid for aid in body.archetype_ids if aid not in archetypes]
    if unknown:
        raise HTTPException(400, f"unknown archetype: {unknown[0]}")
    results = [
        live.engine_for(
            body.input.model_copy(update={"archetype_id": aid, "unit_scale": archetypes[aid]["unit_scale"]["default"]}),
            session,
            with_path_to_yes=False,
        )
        for aid in body.archetype_ids
    ]
    try:
        summary = explain_comparison(results, body.input.language)
    except Exception:  # LLM down: numbers still show, summary is empty
        summary = ""
    return Comparison(results=results, summary=summary, language=body.input.language)
