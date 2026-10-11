import json
import logging
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from api import db
from api.contracts import EngineResult, IntakeInput, Language, Report, ReportCreated, ReportSummary, StageEvent, UserOut
from api.demo_seed import demo_explanation, is_demo
from api.deps import current_user, get_session, require_user
from api.pipeline import run_pipeline
from llm.explain import explain_report

router = APIRouter(prefix="/api/reports", tags=["reports"])
log = logging.getLogger(__name__)


def _sse(kind: str, data: str) -> str:
    return f"event: {kind}\ndata: {data}\n\n"


def _play(report_id: str, intake: IntakeInput) -> Iterator[str]:
    """Runs the real pipeline (it stores stages, engine result and explanation itself) and streams each stage."""
    try:
        for event in run_pipeline(report_id, intake):
            yield _sse("stage", event.model_dump_json())
    except Exception:
        log.exception("pipeline failed for report %s", report_id)
        yield _sse("error", json.dumps({"report_id": report_id}))
        return
    yield _sse("done", json.dumps({"report_id": report_id}))


def _replay(row: db.Report) -> Iterator[str]:
    """A done report replays its stored events immediately, without re-running anything."""
    for event in row.stages:
        yield _sse("stage", StageEvent.model_validate(event).model_dump_json())
    yield _sse("done", json.dumps({"report_id": row.id}))


def _readable_row(report_id: str, user: UserOut | None, session: Session) -> db.Report:
    row = session.get(db.Report, report_id)
    # guest reports (owner_id None) stay open to whoever holds the id; owned ones only to their owner
    if row is None or (row.owner_id is not None and (user is None or user.id != row.owner_id)):
        raise HTTPException(404, "report not found")
    return row


def _to_contract(row: db.Report) -> Report:
    return Report(
        id=row.id,
        status=row.status,
        input=IntakeInput.model_validate(row.input),
        engine=row.engine,
        explanation=row.explanation,
        created_at=row.created_at.isoformat(),
        owner_id=row.owner_id,
    )


@router.post("", response_model=ReportCreated)
def create_report(
    body: IntakeInput,
    user: UserOut | None = Depends(current_user),
    session: Session = Depends(get_session),
):
    row = db.Report(status="pending", input=body.model_dump(mode="json"), owner_id=user.id if user else None)
    session.add(row)
    session.commit()
    return ReportCreated(report_id=row.id)


@router.get("", response_model=list[ReportSummary])
def list_reports(user: UserOut = Depends(require_user), session: Session = Depends(get_session)):
    rows = session.exec(
        select(db.Report).where(db.Report.owner_id == user.id).order_by(db.Report.created_at.desc())
    ).all()
    names = {v.code: v.name for v in session.exec(select(db.Village)).all()}
    return [
        ReportSummary(
            id=row.id,
            archetype_id=row.input["archetype_id"],
            village_name=names.get(row.input["village_code"], row.input["village_code"]),
            verdict=row.engine["verdict"]["level"] if row.engine else None,
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]


@router.get(
    "/{report_id}/stream",
    # documents the `stage` event payload so StageEvent lands in the OpenAPI schema
    responses={200: {"model": StageEvent, "content": {"text/event-stream": {}}}},
)
def stream_report(
    report_id: str,
    user: UserOut | None = Depends(current_user),
    session: Session = Depends(get_session),
):
    row = _readable_row(report_id, user, session)
    if row.status == "done":
        return StreamingResponse(_replay(row), media_type="text/event-stream")
    # shortcut: two streams opened at once on a pending report both run and the last write wins
    return StreamingResponse(_play(row.id, IntakeInput.model_validate(row.input)), media_type="text/event-stream")


@router.post("/{report_id}/explanation", response_model=Report)
def rewrite_explanation(
    report_id: str,
    language: Language | None = None,
    user: UserOut | None = Depends(current_user),
    session: Session = Depends(get_session),
):
    """Writes the explanation again from the stored engine result; the numbers never change.

    `language` (optional) writes it in another language, e.g. after the Entrepreneur switches language on the report page.
    """
    row = _readable_row(report_id, user, session)
    if row.engine is None:
        raise HTTPException(409, "report has no engine result yet")
    intake = IntakeInput.model_validate(row.input)
    result = EngineResult.model_validate(row.engine)
    try:
        if is_demo(report_id):  # the seeded demo reports carry hardcoded text in every language, no LLM call
            explanation = demo_explanation(report_id, language or intake.language, result.figures)
        else:
            explanation = explain_report(result, language or intake.language)
    except Exception:
        log.exception("explain_report failed for report %s", report_id)
        raise HTTPException(503, "explanation unavailable")
    if explanation.available:
        row.explanation = explanation.model_dump(mode="json")
        session.add(row)
        session.commit()
    return _to_contract(row)


@router.get("/{report_id}", response_model=Report)
def get_report(
    report_id: str,
    user: UserOut | None = Depends(current_user),
    session: Session = Depends(get_session),
):
    return _to_contract(_readable_row(report_id, user, session))
