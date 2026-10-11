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

# shortcut: fixed pause between replayed stage events, real pacing comes from run_pipeline in V2
STAGE_DELAY_S = 0.25


def _replay_fixture_stages(report_id: str, events: list[StageEvent]) -> Iterator[str]:
    """V1 only: streams the canned stage events, then `done`. V3 deletes this."""
    for event in events:
        yield f"event: stage\ndata: {event.model_dump_json()}\n\n"
        time.sleep(STAGE_DELAY_S)
    yield f"event: done\ndata: {json.dumps({'report_id': report_id})}\n\n"


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
def stream_report(report_id: str):
    events = [StageEvent.model_validate(e) for e in fixture("stage_events.json")]
    return StreamingResponse(_replay_fixture_stages(report_id, events), media_type="text/event-stream")


@router.get("/{report_id}", response_model=Report)
def get_report(
    report_id: str,
    user: UserOut | None = Depends(current_user),
    session: Session = Depends(get_session),
):
    row = session.get(db.Report, report_id)
    # guest reports (owner_id None) stay open to whoever holds the id; owned ones only to their owner
    if row is None or (row.owner_id is not None and (user is None or user.id != row.owner_id)):
        raise HTTPException(404, "report not found")
    return _to_contract(row)
