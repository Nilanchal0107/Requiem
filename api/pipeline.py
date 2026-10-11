"""The real pipeline driver. Not reachable while USE_FIXTURES=1; V3 swaps it into api/reports.py `_run_stages`."""
import logging
import time
from collections.abc import Iterator
from datetime import date

from sqlmodel import Session

from api import db
from api.contracts import Explanation, IntakeInput, Language, StageEvent, Swot
from data.loaders import load_archetypes, load_schemes
from engine import run_engine
from llm.explain import explain_report

log = logging.getLogger(__name__)


def _unavailable(language: Language) -> Explanation:
    return Explanation(
        language=language,
        sections=[],
        swot=Swot(strengths=[], weaknesses=[], opportunities=[], threats=[]),
        verified=0,
        total=0,
        regenerated=False,
        available=False,
    )


def run_pipeline(report_id: str, intake: IntakeInput) -> Iterator[StageEvent]:
    """Runs the six stages for one report, yielding each StageEvent and saving it on the report as it goes.

    Stores the engine result, explanation and final status itself. An engine failure yields a `failed` stage,
    sets the report `failed` and re-raises so the route can send `error`. An LLM failure yields a `failed`
    explanation stage, stores an unavailable Explanation, and still finishes `done`.
    """
    with Session(db.engine) as session:
        row = session.get(db.Report, report_id)
        if row is None:
            raise LookupError(f"unknown report {report_id}")  # the stream route 404s before calling this
        row.status, row.stages = "running", []

        def emit(stage, status, started=None, sources=(), message=None) -> StageEvent:
            duration = None if started is None else int((time.perf_counter() - started) * 1000)
            event = StageEvent(stage=stage, status=status, duration_ms=duration, sources=list(sources), message=message)
            row.stages = [*row.stages, event.model_dump(mode="json")]  # reassigned so the JSON column sees the change
            session.add(row)
            session.commit()
            return event

        stage = "intake"
        try:
            yield emit(stage, "running", message="Reading your inputs")
            started = time.perf_counter()
            archetype = {a.id: a for a in load_archetypes()}[intake.archetype_id]
            schemes = load_schemes()
            village = session.get(db.Village, intake.village_code)
            if village is None:
                raise LookupError(f"unknown village {intake.village_code}")
            yield emit(stage, "done", started, ["User-entered"])

            stage = "market"
            yield emit(stage, "running", message="Checking the Locality")
            started = time.perf_counter()
            result = run_engine(
                intake,
                archetype.model_dump(mode="json"),
                [s.model_dump(mode="json") for s in schemes],
                village.model_dump(),
                current_year=date.today().year,
            )
            yield emit(stage, "done", started, ["Census 2011", "OpenStreetMap", "archetypes.json (assumptions)"])

            # ponytail: run_engine is one call (known conflict 5), so market carries the whole engine time and the
            # next three stages have no duration; split run_engine into stage calls if per-stage timing matters
            verified = min((s.verified_on for s in schemes), default=None)
            for stage, message, sources in (
                ("cost", "Working out the Project Cost", ["archetypes.json (assumptions)"]),
                ("schemes", "Matching Schemes", [f"schemes.json (verified {verified})"]),
                ("dpr", "Building the DPR", ["Calculation engine"]),
            ):
                yield emit(stage, "running", message=message)
                yield emit(stage, "done", sources=sources)
        except Exception:
            yield emit(stage, "failed", message="Something went wrong while building your report")
            row.status = "failed"
            session.add(row)
            session.commit()
            raise

        yield emit("explanation", "running", message="Writing your explanation")
        started = time.perf_counter()
        try:
            explanation = explain_report(result, intake.language)
        except Exception:
            log.exception("explain_report failed for report %s", report_id)
            explanation = _unavailable(intake.language)
        # ponytail: explain_report has no progress hook, so the retry is reported after it happened
        if explanation.regenerated:
            yield emit("explanation", "retrying", message="Raw number found, regenerating")
        if explanation.available:
            yield emit("explanation", "done", started, ["LLM explanation"])
        else:
            yield emit("explanation", "failed", started, message="Explanation unavailable, the numbers are complete")

        row.engine, row.explanation, row.status = (
            result.model_dump(mode="json"),
            explanation.model_dump(mode="json"),
            "done",
        )
        session.add(row)
        session.commit()
