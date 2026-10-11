import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from api import db, live
from api.contracts import ChatRequest, ChatResponse, IntakeInput
from api.deps import get_session
from api.reports import _to_contract
from llm.chat import chat as run_chat

router = APIRouter(prefix="/api", tags=["chat"])
log = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, session: Session = Depends(get_session)):
    row = session.get(db.Report, body.report_id)
    if row is None or row.engine is None:
        raise HTTPException(404, "report not found")
    report = _to_contract(row)
    intake = IntakeInput.model_validate(row.input)
    try:
        return run_chat(
            report, body.message, body.history[-10:], body.language,
            index=live.scheme_index(),
            what_if=lambda changes: live.engine_for(live.apply_changes(intake, changes), session, with_path_to_yes=False),
        )
    except HTTPException:
        raise
    except Exception:
        log.exception("chat failed for report %s", body.report_id)
        raise HTTPException(503, "chat unavailable, the report numbers are complete")
