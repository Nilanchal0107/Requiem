"""Path to Yes: single changes that reach feasible on their own (TRD §5.8). Pure: no I/O, no LLM, no DB."""
from collections.abc import Callable
from typing import Any

from api.contracts import Change, EngineResult, IntakeInput, PathToYes

OWN_CONTRIBUTION_STEP = 5_000


def find_path_to_yes(
    input: IntakeInput,
    archetype: dict[str, Any],
    base: EngineResult,
    run: Callable[[IntakeInput], EngineResult],
    max_tenure_months: int | None,
) -> PathToYes:
    """Search Own Contribution, unit scale and tenure one change at a time (TRD §5.8).

    `run` is a no-path-to-yes engine run supplied by run_engine, so this module never imports it.
    """
    assert base.verdict.level != "feasible", "Path to Yes only runs for a non-feasible Verdict"
    changes: list[Change] = []

    def try_value(field: str, from_value: float, to_value: float) -> bool:
        res = run(input.model_copy(update={field: to_value}))
        if res.verdict.level != "feasible":
            return False
        changes.append(Change(field=field, from_value=from_value, to_value=to_value, resulting_verdict="feasible"))
        return True

    # Own Contribution: up in ₹5,000 steps, never above the Project Cost.
    project_cost = int(base.cost.project_cost.value)
    oc = input.own_contribution
    while oc < project_cost:
        oc = min(oc + OWN_CONTRIBUTION_STEP, project_cost)
        if try_value("own_contribution", input.own_contribution, oc):
            break

    # Unit scale: down by the Archetype step to its minimum.
    scale = archetype["unit_scale"]
    value = input.unit_scale - scale["step"]
    while value >= scale["min"]:
        if try_value("unit_scale", input.unit_scale, value):
            break
        value -= scale["step"]

    # Tenure: only the best Scheme's maximum.
    best = base.schemes.best
    if best and max_tenure_months and max_tenure_months > best.terms.tenure_months:
        try_value("tenure_months", best.terms.tenure_months, max_tenure_months)

    for c in changes:
        assert c.resulting_verdict == "feasible"
    return PathToYes(changes=changes)
