"""Pure engine: code computes every number, Scheme match and Verdict (ADR 0001).

Order follows the report pipeline: market → cost → schemes → finance → verdict → path to yes.
"""
from typing import Any

from api.contracts import EngineResult, IntakeInput
from engine.cost import build_cost
from engine.figures import FigureRegistry
from engine.finance import (
    break_even_month,
    build_means_of_finance,
    min_dscr,
    monthly_operating,
    payback_months,
    project_years,
    repayment_schedule,
)
from engine.market import analyse_market
from engine.path_to_yes import find_path_to_yes
from engine.schemes import match_schemes
from engine.verdict import decide_verdict


def run_engine(
    input: IntakeInput,
    archetype: dict[str, Any],
    schemes: list[dict[str, Any]],
    village: dict[str, Any],
    *,
    current_year: int,
    with_path_to_yes: bool = True,
) -> EngineResult:
    """Build the whole DPR. `current_year` is passed in so the engine never reads the clock (TRD §5.2)."""
    reg = FigureRegistry()
    market = analyse_market(input, archetype, village, reg, current_year=current_year)
    cost = build_cost(input, archetype, market, reg)
    project_cost = int(cost.project_cost.value)  # Figure.value is float; money fields are whole rupees
    match = match_schemes(input, archetype, schemes, project_cost)
    best = match.best
    best_scheme = next((s for s in schemes if best and s["id"] == best.scheme_id), None)
    finance = build_means_of_finance(input, cost, best, reg)
    schedule = (
        repayment_schedule(best.terms, best_scheme, int(finance.subsidy.value))
        if best and best_scheme
        else []
    )
    ops = monthly_operating(input, archetype, market)
    projections = project_years(input, archetype, market, cost, schedule)
    payback = payback_months(ops, project_cost, reg)
    dscr = min_dscr(projections, reg)
    verdict = decide_verdict(archetype, market, dscr, payback, match)
    base = EngineResult(
        archetype_id=archetype["id"],
        village_code=village["code"],
        market=market,
        cost=cost,
        finance=finance,
        schemes=match,
        repayment=schedule,
        projections=projections,
        break_even_month=break_even_month(ops, schedule, reg),
        payback_months=payback,
        min_dscr=dscr,
        verdict=verdict,
        path_to_yes=None,
        figures=reg.as_dict(),
    )
    if not with_path_to_yes or verdict.level == "feasible":
        return base
    path = find_path_to_yes(
        input,
        archetype,
        base,
        lambda changed: run_engine(
            changed, archetype, schemes, village, current_year=current_year, with_path_to_yes=False
        ),
        best_scheme.get("max_tenure_months") if best_scheme else None,
    )
    return base.model_copy(update={"path_to_yes": path})
