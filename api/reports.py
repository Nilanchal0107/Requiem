import json
import time
import uuid
from collections.abc import Iterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.contracts import IntakeInput, Report, ReportCreated, ReportSummary, StageEvent
from api.deps import require_user
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


def _demo_report(report_id: str | None = None) -> Report:
    """V1 only: the fixture report, optionally under a requested id."""
    data = fixture("report.json")
    return Report.model_validate({**data, "id": report_id} if report_id else data)


@router.post("", response_model=ReportCreated)
def create_report(body: IntakeInput):
    # shortcut: nothing persisted in V1, the id is only handed back; V2 saves the report and starts run_pipeline
    return ReportCreated(report_id=str(uuid.uuid4()))


@router.get("", response_model=list[ReportSummary], dependencies=[Depends(require_user)])
def list_reports():
    report = _demo_report()
    village = next(v for v in fixture("localities.json")["villages"] if v["code"] == report.input.village_code)
    return [
        ReportSummary(
            id=report.id,
            archetype_id=report.input.archetype_id,
            village_name=village["name"],
            verdict=report.engine.verdict.level if report.engine else None,
            created_at=report.created_at,
        )
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
def get_report(report_id: str):
    return _demo_report(report_id)
