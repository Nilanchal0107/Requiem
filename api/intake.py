from fastapi import APIRouter, HTTPException

from api.contracts import IntakeParseRequest, IntakeParseResponse

router = APIRouter(prefix="/api/intake", tags=["intake"])


@router.post("/parse", response_model=IntakeParseResponse)
def parse(body: IntakeParseRequest):
    raise HTTPException(501)
