from fastapi import APIRouter, HTTPException

from api.contracts import EngineResult, IntakeInput

router = APIRouter(prefix="/api", tags=["simulate"])


@router.post("/simulate", response_model=EngineResult)
def simulate(body: IntakeInput):
    raise HTTPException(501)
