"""Project Cost and working capital (TRD §5.1). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import CostBreakdown, IntakeInput, MarketAnalysis
from engine.figures import FigureRegistry


def build_cost(
    input: IntakeInput,
    archetype: dict[str, Any],
    market: MarketAnalysis,
    reg: FigureRegistry,
) -> CostBreakdown:
    """Cost items (fixed + per_unit × unit_scale), working capital and project_cost (TRD §5.1).

    Adds `cost.<item_id>`, `working_capital` and `project_cost` to `reg`.
    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.cost.build_cost")
