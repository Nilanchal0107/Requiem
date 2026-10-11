"""Tests for Ticket 02: Engine market, Project Cost and Funding Gap."""
import json
from pathlib import Path
import pytest

from api.contracts import Figure, IntakeInput
from engine.figures import FigureRegistry
from engine.market import households_now, our_capacity, sales_ceiling, analyse_market
from engine.cost import build_cost
from engine.finance import build_means_of_finance

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def dairy_archetype():
    p = ROOT / "data" / "archetypes" / "dairy.json"
    return json.loads(p.read_text())


@pytest.fixture
def kirana_archetype():
    p = ROOT / "data" / "archetypes" / "kirana.json"
    return json.loads(p.read_text())


@pytest.fixture
def lasalgaon_village():
    p = ROOT / "data" / "census" / "niphad_villages.json"
    villages = json.loads(p.read_text())
    osm = json.loads((ROOT / "data" / "osm" / "niphad_counts.json").read_text())
    v = [x for x in villages if x["name"] == "Lasalgaon"][0]
    return {**v, "osm_counts": osm.get(v["code"], {})}


@pytest.fixture
def dairy_input():
    return IntakeInput(
        village_code="563424",
        archetype_id="dairy",
        unit_scale=5.0,
        own_contribution=100000,
        eligibility={
            "age": 34,
            "gender": "female",
            "social_category": "obc",
            "education": "10th_pass",
            "business_status": "new",
            "prior_subsidy": False,
            "prior_tarun_repaid": False,
            "artisan_trade": False,
            "farmland": "none",
        },
    )


@pytest.fixture
def kirana_input():
    return IntakeInput(
        village_code="563424",
        archetype_id="kirana",
        unit_scale=50000.0,
        own_contribution=20000,
        eligibility={
            "age": 30,
            "gender": "male",
            "social_category": "general",
            "education": "12th_pass",
            "business_status": "new",
            "prior_subsidy": False,
            "prior_tarun_repaid": False,
            "artisan_trade": False,
            "farmland": "none",
        },
    )


def test_registry_rejects_duplicate_figure_id():
    reg = FigureRegistry()
    f1 = Figure(id="test_id", label="Test", value=100.0, unit="INR", source="computed")
    reg.add(f1)
    f2 = Figure(id="test_id", label="Duplicate", value=200.0, unit="INR", source="computed")
    with pytest.raises(ValueError, match="already registered"):
        reg.add(f2)


def test_dairy_project_cost_and_funding_gap_hand_worked(dairy_input, dairy_archetype, lasalgaon_village):
    reg = FigureRegistry()
    market = analyse_market(dairy_input, dairy_archetype, lasalgaon_village, reg, current_year=2026)
    cost = build_cost(dairy_input, dairy_archetype, market, reg)
    means = build_means_of_finance(dairy_input, cost, None, reg)

    # Hand-worked values:
    # Animals: 5 * 70,000 = 350,000
    # Shed: 60,000 + 5 * 10,000 = 110,000
    # Monthly target revenue: 5 * 240 * 0.90 * 45 = 48,600
    # Monthly opex: 48,600 * 0.55 + 2,000 = 28,730
    # Working capital (2 months): 2 * 28,730 = 57,460
    # Project cost: 350,000 + 110,000 + 57,460 = 517,460
    # Own contribution: 100,000
    # Funding gap: 517,460 - 100,000 = 417,460
    assert cost.project_cost.value == 517460
    assert means.funding_gap.value == 417460
    assert means.own_contribution.value == 100000


def test_dairy_aggregator_mode_skips_market_gap(dairy_input, dairy_archetype, lasalgaon_village):
    reg = FigureRegistry()
    market = analyse_market(dairy_input, dairy_archetype, lasalgaon_village, reg, current_year=2026)
    assert market.market_gap.value == 0
    assert market.market_gap.note == "Aggregator mode: replaced by 'aggregator within reach'"
    assert market.potential_customers.value == 0
    assert market.demand.value == 0


def test_kirana_local_mode_computes_market_gap(kirana_input, kirana_archetype, lasalgaon_village):
    reg = FigureRegistry()
    market = analyse_market(kirana_input, kirana_archetype, lasalgaon_village, reg, current_year=2026)
    # Kirana is local mode:
    # households_now = round(5872 * (1.012)^15) = 7020
    # potential_customers = round(7020 * 0.6) = 4212
    # demand = 4212 * 1 = 4212
    # competitors = 12 (from osm counts)
    # competitor_capacity = 12 * 80 = 960
    # market_gap = 4212 - 960 = 3252
    assert market.market_gap.value > 0
    assert market.market_gap.formula == "demand - competitor_capacity"
    assert market.potential_customers.value > 0
    assert market.demand.value > 0


def test_every_money_figure_is_whole_rupees(dairy_input, dairy_archetype, lasalgaon_village):
    reg = FigureRegistry()
    market = analyse_market(dairy_input, dairy_archetype, lasalgaon_village, reg, current_year=2026)
    cost = build_cost(dairy_input, dairy_archetype, market, reg)
    means = build_means_of_finance(dairy_input, cost, None, reg)

    for fig in reg.as_dict().values():
        if fig.unit == "INR":
            assert fig.value.is_integer(), f"Figure {fig.id} value {fig.value} is not a whole number of rupees"
