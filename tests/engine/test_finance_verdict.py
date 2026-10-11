"""Tests for Ticket 03: Engine Scheme match, loan, repayment, projections, and Verdict."""
import json
from pathlib import Path
import pytest

from api.contracts import EngineResult, Figure, IntakeInput
from engine import run_engine
from engine.figures import FigureRegistry
from engine.finance import build_loan_terms, repayment_schedule
from engine.schemes import match_schemes
from engine.verdict import decide_verdict
from engine.market import analyse_market

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
def schemes():
    return [
        json.loads((ROOT / "data" / "schemes" / "mudra.json").read_text()),
        json.loads((ROOT / "data" / "schemes" / "pmegp.json").read_text()),
        json.loads((ROOT / "data" / "schemes" / "standup_india.json").read_text()),
    ]


@pytest.fixture
def villages():
    raw_villages = json.loads((ROOT / "data" / "census" / "niphad_villages.json").read_text())
    osm = json.loads((ROOT / "data" / "osm" / "niphad_counts.json").read_text())
    return [{**v, "osm_counts": osm.get(v["code"], {})} for v in raw_villages]


def test_emi_matches_hand_checked_bank_calculator(schemes):
    mudra = next(s for s in schemes if s["id"] == "mudra")
    # Principal 417,460, 10% annual interest, 60 months tenure, 6 months serviced moratorium
    # n = 54 months. r = 10 / 1200.
    # Hand-checked standard EMI = 9,632.
    terms = build_loan_terms(417460, mudra, tenure_months=60)
    assert terms.emi == 9632
    assert terms.total_interest == 123530


def test_repayment_schedule_closes_at_exactly_zero(schemes):
    mudra = next(s for s in schemes if s["id"] == "mudra")
    terms = build_loan_terms(417460, mudra, tenure_months=60)
    schedule = repayment_schedule(terms, mudra, subsidy=0)
    assert len(schedule) == 60
    assert schedule[-1].closing == 0


def test_pmegp_subsidy_reduces_balance_at_end_of_lock_in_only(schemes):
    pmegp = next(s for s in schemes if s["id"] == "pmegp")
    # Principal 1,000,000, 84 months tenure, 6 months moratorium, 36 months lock-in
    terms = build_loan_terms(1000000, pmegp, tenure_months=84)
    subsidy_amt = 350000  # 35%
    schedule = repayment_schedule(terms, pmegp, subsidy=subsidy_amt)
    assert len(schedule) == 84

    # At month 35, no subsidy applied yet
    # At month 36 (lock-in), closing balance drops by subsidy
    row_35 = schedule[34]
    row_36 = schedule[35]
    # Expected closing at 36 before subsidy would be row_36.opening - (emi - interest)
    raw_closing_36 = row_36.opening - (row_36.payment - row_36.interest)
    assert row_36.closing == raw_closing_36 - subsidy_amt
    assert schedule[-1].closing == 0


def test_mudra_tier_selection_on_boundary_edges(schemes, dairy_archetype):
    mudra_scheme = [s for s in schemes if s["id"] == "mudra"]

    # Shishu: max 50,000
    inp_shishu = IntakeInput(
        village_code="563424",
        archetype_id="dairy",
        unit_scale=2.0,
        own_contribution=0,
        eligibility={"age": 25, "gender": "male", "social_category": "general", "education": "10th_pass", "business_status": "new"},
    )
    m_50k = match_schemes(inp_shishu, dairy_archetype, mudra_scheme, project_cost=50000)
    assert m_50k.best is not None
    assert m_50k.best.tier == "shishu"

    # Just above 50,000 -> Kishore
    m_50001 = match_schemes(inp_shishu, dairy_archetype, mudra_scheme, project_cost=50001)
    assert m_50001.best is not None
    assert m_50001.best.tier == "kishore"

    # Kishore upper bound: 500,000
    m_500k = match_schemes(inp_shishu, dairy_archetype, mudra_scheme, project_cost=500000)
    assert m_500k.best is not None
    assert m_500k.best.tier == "kishore"

    # Just above 500,000 -> Tarun
    m_500001 = match_schemes(inp_shishu, dairy_archetype, mudra_scheme, project_cost=500001)
    assert m_500001.best is not None
    assert m_500001.best.tier == "tarun"


def test_own_contribution_below_minimum_produces_unlock_hint(schemes, kirana_archetype):
    # Stand-Up India requires 10% own contribution
    # Project cost 1,200,000. Own contribution 50,000 (needs 120,000).
    su_schemes = [s for s in schemes if s["id"] == "standup_india"]
    inp = IntakeInput(
        village_code="563424",
        archetype_id="kirana",
        unit_scale=50000,
        own_contribution=50000,
        eligibility={"age": 30, "gender": "female", "social_category": "general", "education": "10th_pass", "business_status": "new"},
    )
    match = match_schemes(inp, kirana_archetype, su_schemes, project_cost=1200000)
    assert match.best is None
    assert len(match.ineligible) == 1
    assert "₹70,000 more Own Contribution" in match.ineligible[0].unlock_hint


def test_verdict_takes_worst_signal(dairy_archetype, villages):
    lasalgaon = villages[0]
    reg = FigureRegistry()
    inp = IntakeInput(
        village_code="563424",
        archetype_id="dairy",
        unit_scale=5.0,
        own_contribution=100000,
        eligibility={"age": 30, "gender": "female", "social_category": "obc", "education": "10th_pass", "business_status": "new"},
    )
    market = analyse_market(inp, dairy_archetype, lasalgaon, reg, current_year=2026)


    # 3 feasible signals, 1 not_feasible (e.g. min_dscr < 1.25)
    f_dscr_bad = Figure(id="min_dscr", label="Lowest DSCR", value=1.10, unit="ratio", source="computed")
    f_payback_good = Figure(id="payback_months", label="Payback", value=24, unit="months", source="computed")

    from api.contracts import LoanTerms, SchemeMatch, SchemeOption
    terms = LoanTerms(principal=400000, interest_rate=10.0, tenure_months=60, moratorium_months=6, moratorium_mode="serviced", emi=9000, total_interest=100000)
    opt = SchemeOption(scheme_id="mudra", name="MUDRA", terms=terms, effective_rate=10.0, reasons=[], source_url="https://example.com")
    schemes_match = SchemeMatch(best=opt, alternatives=[], ineligible=[])

    verdict = decide_verdict(dairy_archetype, market, f_dscr_bad, f_payback_good, schemes_match)
    assert verdict.level == "not_feasible"
    dscr_signal = next(s for s in verdict.signals if s.name == "dscr")
    assert dscr_signal.level == "not_feasible"


def test_run_engine_returns_contract_valid_for_all_six_cases(dairy_archetype, kirana_archetype, schemes, villages):
    for v in villages:
        for arch in [dairy_archetype, kirana_archetype]:
            unit_scale = arch["unit_scale"]["default"]
            own_contrib = 100000 if arch["id"] == "dairy" else 20000
            inp = IntakeInput(
                village_code=v["code"],
                archetype_id=arch["id"],
                unit_scale=unit_scale,
                own_contribution=own_contrib,
                eligibility={
                    "age": 30,
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
            res = run_engine(inp, arch, schemes, v, current_year=2026, with_path_to_yes=False)
            assert isinstance(res, EngineResult)
            assert res.archetype_id == arch["id"]
            assert res.village_code == v["code"]
            assert res.verdict.level in ("feasible", "feasible_with_changes", "not_feasible")
            assert len(res.figures) > 10
