from fastapi import APIRouter

from api.contracts import IntakeParseRequest, IntakeParseResponse
from api.settings import fixture

router = APIRouter(prefix="/api/intake", tags=["intake"])


# shortcut: ignores the text and returns the fixture report's archetype and scale; V2 runs the LLM extractor
@router.post("/parse", response_model=IntakeParseResponse)
def parse(body: IntakeParseRequest):
    inp = fixture("report.json")["input"]
    return IntakeParseResponse(
        fields={"archetype_id": inp["archetype_id"], "unit_scale": inp["unit_scale"], "language": body.language},
        missing=["village_code", "own_contribution", "eligibility.age", "eligibility.gender", "eligibility.social_category", "eligibility.education"],
    )
