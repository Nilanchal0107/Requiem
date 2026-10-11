import json
import time
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from api import db
from api.contracts import IntakeInput, Report, ReportCreated, ReportSummary, StageEvent, UserOut
from api.deps import current_user, get_session, require_user
from api.settings import fixture

router = APIRouter(prefix="/api/reports", tags=["reports"])

# shortcut: fixed pause between fixture stage events, real pacing comes from run_pipeline in V3
STAGE_DELAY_S = 0.25


def _sse(kind: str, data: str) -> str:
    return f"event: {kind}\ndata: {data}\n\n"


def _run_stages(report_id: str, intake: IntakeInput) -> Iterator[StageEvent]:
    """Fixture stand-in for the pipeline: the canned stage events, paced."""
    # shortcut: V3 swaps this body for `yield from run_pipeline(report_id, intake)` (api/pipeline.py)
    for event in fixture("stage_events.json"):
        yield StageEvent.model_validate(event)
        time.sleep(STAGE_DELAY_S)


def _play_and_store(row: db.Report, session: Session, demo: dict) -> Iterator[str]:
    """Streams each stage as it runs, then stores the events, engine result and explanation on the report."""
    # shortcut: no `error` event or `failed` status yet (fixtures can't fail); V3's run_pipeline adds both
    stages = []
    for event in _run_stages(row.id, IntakeInput.model_validate(row.input)):
        stages.append(event.model_dump(mode="json"))
        yield _sse("stage", event.model_dump_json())
    # shortcut: result and explanation are the fixture's; V3's run_pipeline stores the real ones itself
    row.stages, row.engine, row.explanation, row.status = stages, demo["engine"], demo["explanation"], "done"
    session.add(row)
    session.commit()
    yield _sse("done", json.dumps({"report_id": row.id}))


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
    # shortcut: village names come from the fixture localities, V3 reads them through the data loaders
    names = {v["code"]: v["name"] for v in fixture("localities.json")["villages"]}
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
    # shortcut: two streams opened at once on a pending report both run and the last write wins;
    # claim the row with status "running" if V3's live pipeline makes that costly
    demo = fixture("report.json")  # loaded before the 200 goes out, so USE_FIXTURES=0 stays a clean 501
    return StreamingResponse(_play_and_store(row, session, demo), media_type="text/event-stream")


@router.get("/{report_id}", response_model=Report)
def get_report(
    report_id: str,
    user: UserOut | None = Depends(current_user),
    session: Session = Depends(get_session),
):
    return _to_contract(_readable_row(report_id, user, session))
