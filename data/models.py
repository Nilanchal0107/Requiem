"""Models for the hand-curated catalogue JSON (TRD §4.1, §4.2). One file per item in data/archetypes/ and data/schemes/."""
from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Op = Literal["eq", "ne", "in", "not_in", "gt", "gte", "lt", "lte"]


class _Strict(BaseModel):
    # A misspelled key in hand-curated JSON must fail loudly, not be silently dropped (e.g. "whn" for "when").
    model_config = ConfigDict(extra="forbid")


class CostItem(_Strict):
    id: str
    name: str
    fixed: float
    per_unit: float
    depreciation_pct: float
    note: str


class UnitScale(_Strict):
    default: int
    min: int
    max: int
    step: int


class Revenue(_Strict):
    unit: str
    output_per_unit_per_month: float
    price: float
    note: str


class OperatingCost(_Strict):
    variable_pct_of_revenue: float
    fixed_monthly: float
    note: str


class Market(_Strict):
    mode: Literal["local", "aggregator"]
    aggregator: str | None = None
    adoption_rate: float | None = None
    units_per_customer_per_month: float | None = None
    competitor_osm_tags: list[str] = []
    capacity_per_competitor: float | None = None


class Archetype(_Strict):
    id: str
    name: str
    sector: str
    unit_label: str
    unit_scale: UnitScale
    eligibility_fields: list[str]
    cost_items: list[CostItem]
    working_capital_months: int
    revenue: Revenue
    operating_cost: OperatingCost
    ramp_up_months: int
    target_utilisation_pct: float
    growth_pct_per_year: float
    market: Market
    channels: list[str]
    notes: str


class Condition(_Strict):
    field: str
    op: Op
    value: Any


class Rule(_Strict):
    field: str
    op: Op
    value: Any
    when: list[Condition] = []
    message: str


class WhenPct(_Strict):
    """One entry of `own_contribution_pct` or `subsidy.rates`. The first entry whose `when` holds applies."""

    pct: float
    when: list[Condition] = []


class Tier(_Strict):
    id: str
    name: str
    max_loan: float
    when: list[Condition] = []


class Loan(_Strict):
    max: float
    interest_rate: float
    rate_source: str
    max_tenure_months: int
    moratorium_months: int
    moratorium_mode: Literal["capitalised", "serviced"]
    repayment_mode: Literal["emi", "bullet"]


class Subsidy(_Strict):
    type: Literal["none", "capital_backended", "capital_upfront", "interest_subvention"]
    lock_in_months: int = 0
    rates: list[WhenPct] = []


class Scheme(_Strict):
    id: str
    name: str
    covers: str
    sectors: list[str]
    # Rule 6: every Scheme rule is traceable to its source page and the date it was checked.
    source_url: str = Field(pattern=r"^https?://\S+$")
    verified_on: date
    rules: list[Rule]
    own_contribution_pct: list[WhenPct]
    loan: Loan
    tiers: list[Tier]
    subsidy: Subsidy
