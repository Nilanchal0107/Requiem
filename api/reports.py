from fastapi import APIRouter, HTTPException

from api.contracts import IntakeInput, Report, ReportCreated, ReportSummary, StageEvent

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("", response_model=ReportCreated)
def create_report(body: IntakeInput):
    raise HTTPException(501)


@router.get("", response_model=list[ReportSummary])
def list_reports():
    raise HTTPException(501)


@router.get(
    "/{report_id}/stream",
    # documents the `stage` event payload so StageEvent lands in the OpenAPI schema
    responses={200: {"model": StageEvent, "content": {"text/event-stream": {}}}},
)
def stream_report(report_id: str):
    raise HTTPException(501)


@router.get("/{report_id}", response_model=Report)
def get_report(report_id: str):
    raise HTTPException(501)
