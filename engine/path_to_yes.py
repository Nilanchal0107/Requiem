"""Path to Yes: single changes that reach feasible on their own (TRD §5.8). Pure: no I/O, no LLM, no DB."""
from collections.abc import Callable
from typing import Any

from api.contracts import EngineResult, IntakeInput, PathToYes


def find_path_to_yes(
    input: IntakeInput,
    archetype: dict[str, Any],
    base: EngineResult,
    run: Callable[[IntakeInput], EngineResult],
    max_tenure_months: int | None,
) -> PathToYes:
    """Search Own Contribution, unit scale and tenure one change at a time (TRD §5.8).

    `run` is a no-path-to-yes engine run supplied by run_engine, so this module never imports it.
    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.path_to_yes.find_path_to_yes")
