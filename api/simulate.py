from fastapi import APIRouter

from api.contracts import EngineResult, IntakeInput
from api.settings import fixture

router = APIRouter(prefix="/api", tags=["simulate"])


# shortcut: returns the fixture report's engine output whatever the intake; V2 swaps in engine.run
@router.post("/simulate", response_model=EngineResult)
def simulate(body: IntakeInput):
    return EngineResult.model_validate(fixture("report.json")["engine"])
