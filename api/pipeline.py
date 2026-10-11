"""The real pipeline driver. Declared in V1, implemented in V2; V1 streams fixture events from api/reports.py instead."""
from collections.abc import Iterator

from api.contracts import IntakeInput, StageEvent


def run_pipeline(report_id: str, intake: IntakeInput) -> Iterator[StageEvent]:
    """Run engine, LLM and persistence for one report, yielding a StageEvent per step."""
    raise NotImplementedError
