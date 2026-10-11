from fastapi import APIRouter

from api import live
from api.contracts import IntakeParseRequest, IntakeParseResponse
from llm.intake import parse_intake

router = APIRouter(prefix="/api/intake", tags=["intake"])


@router.post("/parse", response_model=IntakeParseResponse)
def parse(body: IntakeParseRequest):
    return parse_intake(body, list(live.archetypes()))
