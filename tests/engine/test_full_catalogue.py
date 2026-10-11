"""Ticket 48: KCC bullet repayment and interest subvention, CMEGP rules, and the full catalogue running end to end."""
import json
from pathlib import Path

from api.contracts import IntakeInput
from engine import run_engine
from engine.finance import build_loan_terms, repayment_schedule
from engine.schemes import match_schemes

ROOT = Path(__file__).resolve().parents[2]


def _load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


ARCHETYPES = {p.stem: _load(f"data/archetypes/{p.name}") for p in (ROOT / "data" / "archetypes").glob("*.json")}
SCHEMES = [_load(f"data/schemes/{p.name}") for p in sorted((ROOT / "data" / "schemes").glob("*.json"))]
SCHEME = {s["id"]: s for s in SCHEMES}
OSM = _load("data/osm/niphad_counts.json")
VILLAGES = [{**v, "osm_counts": OSM[v["code"]]} for v in _load("data/census/niphad_villages.json")]
WOMAN = {"age": 30, "gender": "female", "social_category": "obc", "education": "10th_pass", "business_status": "new"}


def _input(archetype_id, own, scale=None, village=0, **elig):
    a = ARCHETYPES[archetype_id]
    return IntakeInput(village_code=VILLAGES[village]["code"], archetype_id=archetype_id,
                       unit_scale=scale or a["unit_scale"]["default"], own_contribution=own, eligibility={**WOMAN, **elig})


def test_bullet_pays_once_at_the_end_and_closes_at_zero():
    kcc = SCHEME["kcc"]
    terms = build_loan_terms(100000, kcc, tenure_months=None)
    assert terms.tenure_months == 12 and terms.moratorium_months == 0
    due = 100000
    for _ in range(12):
        due += round(due * 0.07 / 12)  # TRD §5.5: P x (1 + r)^tenure, rounded per month
    assert terms.emi == due and terms.total_interest == due - 100000
    rows = repayment_schedule(terms, kcc, subsidy=0)
    assert [r.payment for r in rows[:-1]] == [0] * 11
    assert rows[-1].payment == due and rows[-1].closing == 0
    assert sum(r.interest for r in rows) == terms.total_interest


def test_interest_subvention_lowers_the_rate_paid_and_ranks_by_it():
    onion = ARCHETYPES["onion_cultivation"]
    match = match_schemes(_input("onion_cultivation", 100000, farmland="owned"), onion, SCHEMES, project_cost=186440)
    assert match.best.scheme_id == "kcc"
    assert match.best.terms.interest_rate == 4.0 and match.best.effective_rate == 4.0   # 7% minus the 3% incentive
    assert {i.scheme_id for i in match.ineligible} >= {"mudra", "pmegp"}                 # crop farming: sector not covered


def test_kcc_needs_farmland_for_a_crop_and_caps_animal_husbandry_at_two_lakh():
    onion = ARCHETYPES["onion_cultivation"]
    no_land = match_schemes(_input("onion_cultivation", 100000), onion, SCHEMES, project_cost=186440)
    assert no_land.best is None and "farmland" in next(i for i in no_land.ineligible if i.scheme_id == "kcc").failed_rule
    dairy = ARCHETYPES["dairy"]
    big = next(i for i in match_schemes(_input("dairy", 100000), dairy, SCHEMES, project_cost=517460).ineligible if i.scheme_id == "kcc")
    assert big.unlock_hint == "₹217,460 more Own Contribution"
    small = match_schemes(_input("dairy", 100000), dairy, [SCHEME["kcc"]], project_cost=250000)
    assert small.best.scheme_id == "kcc"


def test_cmegp_negative_list_age_rule_and_back_ended_subsidy():
    kirana, dairy = ARCHETYPES["kirana"], ARCHETYPES["dairy"]
    cmegp = [SCHEME["cmegp"]]
    assert "negative list" in match_schemes(_input("dairy", 100000), dairy, cmegp, 517460).ineligible[0].failed_rule
    assert match_schemes(_input("kirana", 50000, age=48), kirana, cmegp, 155200).best is not None            # woman: limit 50
    man = {"gender": "male", "social_category": "general", "age": 48}
    assert "45" in match_schemes(_input("kirana", 50000, **man), kirana, cmegp, 155200).ineligible[0].failed_rule
    res = run_engine(_input("kirana", 50000), kirana, SCHEMES, VILLAGES[0], current_year=2026)
    if res.schemes.best.scheme_id == "cmegp":
        assert res.finance.subsidy_backended and res.finance.subsidy.value == round(155200 * 0.35)


def test_pm_vishwakarma_is_five_percent_and_only_for_a_listed_trade():
    tailoring = ARCHETYPES["tailoring"]
    res = run_engine(_input("tailoring", 20000, artisan_trade=True), tailoring, SCHEMES, VILLAGES[0], current_year=2026)
    assert res.schemes.best.scheme_id == "pm_vishwakarma" and res.schemes.best.terms.interest_rate == 5.0
    other = match_schemes(_input("tailoring", 20000), tailoring, [SCHEME["pm_vishwakarma"]], 76500)
    assert other.best is None and "traditional trades" in other.ineligible[0].failed_rule


def test_every_archetype_runs_end_to_end_with_a_sound_result():
    for aid, a in ARCHETYPES.items():
        for v in VILLAGES:
            elig = {"farmland": "owned", "artisan_trade": True}
            inp = _input(aid, 100000, village=VILLAGES.index(v), **elig)
            res = run_engine(inp, a, SCHEMES, v, current_year=2026)
            assert res.schemes.best is not None, f"{aid} in {v['name']}: no Scheme matched"
            assert not res.repayment or res.repayment[-1].closing == 0   # no schedule when Own Contribution covers it all
            assert res.cost.project_cost.value > 0
            assert not res.repayment or res.min_dscr.value > 0   # with no loan DSCR is 0.0 (open in TRD §5.6)


def test_a_twelve_month_revolving_loan_is_not_judged_on_twelve_month_payback():
    onion = ARCHETYPES["onion_cultivation"]
    res = run_engine(_input("onion_cultivation", 120000, farmland="owned"), onion, SCHEMES, VILLAGES[0], current_year=2026)
    assert res.payback_months.value > 12
    assert next(s for s in res.verdict.signals if s.name == "payback").level == "feasible"
