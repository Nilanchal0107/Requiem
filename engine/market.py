"""Market sizing (TRD §5.2). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import IntakeInput, MarketAnalysis
from engine.figures import FigureRegistry

CENSUS_BASE_YEAR = 2011
HOUSEHOLD_GROWTH = 0.012      # assumption: 1.2 %/yr
MIN_WINNABLE_SHARE = 0.3      # assumption: 30 % of our capacity is winnable


def households_now(census_households: int, current_year: int) -> float:
    """Census 2011 households grown at HOUSEHOLD_GROWTH per year.

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.market.households_now")


def our_capacity(input: IntakeInput, archetype: dict[str, Any]) -> float:
    """unit_scale × output_per_unit_per_month, in the archetype's revenue unit.

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.market.our_capacity")


def sales_ceiling(input: IntakeInput, archetype: dict[str, Any], market: MarketAnalysis) -> float:
    """Local mode: max(market_gap, 0.3 × our_capacity). Aggregator mode: our_capacity.

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.market.sales_ceiling")


def analyse_market(
    input: IntakeInput,
    archetype: dict[str, Any],
    village: dict[str, Any],
    reg: FigureRegistry,
    *,
    current_year: int,
) -> MarketAnalysis:
    """Households, demand, competitors, market gap and competitor coverage (TRD §5.2).

    Adds each Figure to `reg`. Competitors use competitor_override, else the OSM count for the archetype.
    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.market.analyse_market")
