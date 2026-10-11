"""Market sizing (TRD §5.2). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import Figure, IntakeInput, MarketAnalysis
from engine.figures import FigureRegistry

CENSUS_BASE_YEAR = 2011
HOUSEHOLD_GROWTH = 0.012      # assumption: 1.2 %/yr
MIN_WINNABLE_SHARE = 0.3      # assumption: 30 % of our capacity is winnable


def households_now(census_households: int, current_year: int) -> float:
    """Census 2011 households grown at HOUSEHOLD_GROWTH per year.

    V2 must add at least one assert check.
    """
    assert census_households >= 0, "census_households must be non-negative"
    assert current_year >= CENSUS_BASE_YEAR, f"current_year must be >= {CENSUS_BASE_YEAR}"
    years = current_year - CENSUS_BASE_YEAR
    return float(round(census_households * ((1.0 + HOUSEHOLD_GROWTH) ** years)))


def our_capacity(input: IntakeInput, archetype: dict[str, Any]) -> float:
    """unit_scale × output_per_unit_per_month, in the archetype's revenue unit.

    V2 must add at least one assert check.
    """
    assert input.unit_scale > 0, "unit_scale must be positive"
    output_per_unit = float(archetype["revenue"]["output_per_unit_per_month"])
    assert output_per_unit > 0, "output_per_unit_per_month must be positive"
    return float(input.unit_scale * output_per_unit)


def sales_ceiling(input: IntakeInput, archetype: dict[str, Any], market: MarketAnalysis) -> float:
    """Local mode: max(market_gap, 0.3 × our_capacity). Aggregator mode: our_capacity.

    V2 must add at least one assert check.
    """
    assert isinstance(market, MarketAnalysis), "market must be MarketAnalysis"
    cap = our_capacity(input, archetype)
    mode = archetype.get("market", {}).get("mode", "local")
    if mode == "aggregator":
        return cap
    gap = market.market_gap.value
    return float(max(gap, MIN_WINNABLE_SHARE * cap))


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
    assert isinstance(input, IntakeInput)
    assert isinstance(archetype, dict)
    assert isinstance(village, dict)
    assert isinstance(reg, FigureRegistry)

    census_hh = int(village.get("households", 0))
    proj_hh = households_now(census_hh, current_year)
    years = current_year - CENSUS_BASE_YEAR

    fig_hh = reg.add(
        Figure(
            id="households",
            label="Households (projected)",
            value=proj_hh,
            unit="households",
            source="computed",
            formula="census_households * (1 + growth)^(current_year - 2011)",
            inputs={
                "census_households": float(census_hh),
                "growth_pct": float(HOUSEHOLD_GROWTH * 100),
                "years": float(years),
            },
        )
    )

    cap_val = our_capacity(input, archetype)
    unit_label = archetype.get("revenue", {}).get("unit", "units")
    reg.add(
        Figure(
            id="our_capacity",
            label=f"Our capacity ({unit_label} per month)",
            value=cap_val,
            unit="count",
            source="computed",
            formula="unit_scale * output_per_unit_per_month",
            inputs={
                "unit_scale": float(input.unit_scale),
                "output_per_unit_per_month": float(archetype["revenue"]["output_per_unit_per_month"]),
            },
        )
    )

    market_cfg = archetype.get("market", {})
    mode = market_cfg.get("mode", "local")

    osm_counts = village.get("osm_counts", {})
    arch_id = archetype.get("id", input.archetype_id)
    osm_comp_count = int(osm_counts.get(arch_id, 0)) if isinstance(osm_counts, dict) else 0

    if input.competitor_override is not None:
        comp_count = int(input.competitor_override)
        comp_source = "user"
        coverage = "ok"
    else:
        comp_count = osm_comp_count
        comp_source = "osm"
        coverage = "low" if comp_count == 0 else "ok"

    if mode == "aggregator":
        fig_pot = reg.add(
            Figure(
                id="potential_customers",
                label="Potential customers",
                value=0.0,
                unit="count",
                source="computed",
                note="Not used in aggregator mode",
            )
        )
        fig_dem = reg.add(
            Figure(
                id="demand",
                label="Demand per month",
                value=0.0,
                unit="count",
                source="computed",
                note="Not used in aggregator mode",
            )
        )
        fig_comp = reg.add(
            Figure(
                id="competitors",
                label="Competitors nearby",
                value=float(comp_count),
                unit="count",
                source=comp_source,
                note=f"No competitor tags for {arch_id}; OSM coverage is low in rural areas" if comp_count == 0 else None,
            )
        )
        fig_comp_cap = reg.add(
            Figure(
                id="competitor_capacity",
                label="Competitor capacity",
                value=0.0,
                unit="count",
                source="computed",
            )
        )
        fig_gap = reg.add(
            Figure(
                id="market_gap",
                label="Market Gap",
                value=0.0,
                unit="count",
                source="computed",
                note="Aggregator mode: replaced by 'aggregator within reach'",
            )
        )
    else:
        adoption = float(market_cfg.get("adoption_rate", 0.0) or 0.0)
        units_per_cust = float(market_cfg.get("units_per_customer_per_month", 0.0) or 0.0)
        cap_per_comp = float(market_cfg.get("capacity_per_competitor", 0.0) or 0.0)

        pot_cust = round(proj_hh * adoption)
        demand_val = round(pot_cust * units_per_cust)
        comp_cap_val = round(comp_count * cap_per_comp)
        gap_val = demand_val - comp_cap_val

        fig_pot = reg.add(
            Figure(
                id="potential_customers",
                label="Potential customers",
                value=float(pot_cust),
                unit="count",
                source="computed",
                formula="households_now * adoption_rate",
                inputs={"households_now": proj_hh, "adoption_rate": adoption},
            )
        )
        fig_dem = reg.add(
            Figure(
                id="demand",
                label="Demand per month",
                value=float(demand_val),
                unit="count",
                source="computed",
                formula="potential_customers * units_per_customer_per_month",
                inputs={"potential_customers": float(pot_cust), "units_per_customer_per_month": units_per_cust},
            )
        )
        fig_comp = reg.add(
            Figure(
                id="competitors",
                label="Competitors nearby",
                value=float(comp_count),
                unit="count",
                source=comp_source,
                note="OSM coverage is low in rural areas" if (comp_source == "osm" and comp_count == 0) else None,
            )
        )
        fig_comp_cap = reg.add(
            Figure(
                id="competitor_capacity",
                label="Competitor capacity",
                value=float(comp_cap_val),
                unit="count",
                source="computed",
                formula="competitors * capacity_per_competitor",
                inputs={"competitors": float(comp_count), "capacity_per_competitor": cap_per_comp},
            )
        )
        fig_gap = reg.add(
            Figure(
                id="market_gap",
                label="Market Gap",
                value=float(gap_val),
                unit="count",
                source="computed",
                formula="demand - competitor_capacity",
                inputs={"demand": float(demand_val), "competitor_capacity": float(comp_cap_val)},
            )
        )

    channels = archetype.get("channels", [])
    return MarketAnalysis(
        households=fig_hh,
        potential_customers=fig_pot,
        demand=fig_dem,
        competitors=fig_comp,
        competitor_capacity=fig_comp_cap,
        market_gap=fig_gap,
        competitor_coverage=coverage,
        channels=channels,
    )

