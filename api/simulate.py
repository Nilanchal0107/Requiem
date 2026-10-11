from fastapi import APIRouter, Depends
from sqlmodel import Session

from api import live
from api.contracts import EngineResult, IntakeInput
from api.deps import get_session

router = APIRouter(prefix="/api", tags=["simulate"])


@router.post("/simulate", response_model=EngineResult)
def simulate(body: IntakeInput, session: Session = Depends(get_session)):
    return live.engine_for(body, session)
