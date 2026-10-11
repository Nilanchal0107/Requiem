"""Project Cost and working capital (TRD §5.1). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import CostBreakdown, CostItem, Figure, IntakeInput, MarketAnalysis
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
    assert isinstance(input, IntakeInput)
    assert isinstance(archetype, dict)
    assert isinstance(market, MarketAnalysis)
    assert isinstance(reg, FigureRegistry)

    cost_items_raw = archetype.get("cost_items", [])
    items = []
    item_figs: dict[str, float] = {}

    for item in cost_items_raw:
        item_id = item["id"]
        name = item["name"]
        fixed = int(item.get("fixed", 0))
        per_unit = int(item.get("per_unit", 0))
        val = int(round(fixed + per_unit * input.unit_scale))

        fig = reg.add(
            Figure(
                id=f"cost.{item_id}",
                label=name,
                value=float(val),
                unit="INR",
                source="assumption",
                formula="fixed + per_unit * unit_scale",
                inputs={
                    "fixed": float(fixed),
                    "per_unit": float(per_unit),
                    "unit_scale": float(input.unit_scale),
                },
                note=item.get("note"),
            )
        )
        items.append(CostItem(name=name, figure=fig))
        item_figs[f"cost.{item_id}"] = float(val)

    # Working capital = working_capital_months × monthly operating cost at target utilisation
    wc_months = int(archetype.get("working_capital_months", 0))
    target_util = float(archetype.get("target_utilisation_pct", 100)) / 100.0

    output_per_unit = float(archetype["revenue"]["output_per_unit_per_month"])
    price = float(archetype["revenue"]["price"])
    monthly_units_target = input.unit_scale * output_per_unit * target_util
    monthly_rev_target = monthly_units_target * price

    op_cfg = archetype.get("operating_cost", {})
    var_pct = float(op_cfg.get("variable_pct_of_revenue", 0)) / 100.0
    fixed_monthly = float(op_cfg.get("fixed_monthly", 0))

    monthly_opex_target = round(monthly_rev_target * var_pct + fixed_monthly)
    wc_val = int(round(wc_months * monthly_opex_target))

    fig_wc = reg.add(
        Figure(
            id="working_capital",
            label="Working capital",
            value=float(wc_val),
            unit="INR",
            source="computed",
            formula="working_capital_months * monthly operating cost at target utilisation",
            inputs={
                "working_capital_months": float(wc_months),
                "monthly_operating_cost": float(monthly_opex_target),
            },
        )
    )

    proj_cost = int(sum(item_figs.values()) + wc_val)
    fig_proj = reg.add(
        Figure(
            id="project_cost",
            label="Project Cost",
            value=float(proj_cost),
            unit="INR",
            source="computed",
            formula="sum of cost items + working_capital",
            inputs={**item_figs, "working_capital": float(wc_val)},
        )
    )

    return CostBreakdown(items=items, project_cost=fig_proj)

