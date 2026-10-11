"""Checks the V1 fixtures (fixtures/) against the frozen contract (api/contracts.py)."""
import json
import re
from pathlib import Path

import pytest

from api.contracts import (
    ArchetypeSummary,
    Block,
    District,
    Eligibility,
    Report,
    SchemeSummary,
    StageEvent,
    Village,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
PLACEHOLDER = re.compile(r"\{\{([a-z0-9_.]+)\}\}")
DIGIT = re.compile(r"[0-9०-९]")  # ASCII and Devanagari digits
FIGURE_KEYS = {"id", "label", "value", "unit", "source"}


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def report():
    return Report.model_validate(load("report.json"))


def explanation_texts(report):
    exp = report.explanation
    return [s.text for s in exp.sections] + exp.swot.strengths + exp.swot.weaknesses + exp.swot.opportunities + exp.swot.threats


def nested_figures(obj):
    """Yield every Figure-shaped dict in the engine output, skipping the registry itself."""
    if isinstance(obj, dict):
        if FIGURE_KEYS <= obj.keys():
            yield obj
        for key, value in obj.items():
            if key != "figures":
                yield from nested_figures(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from nested_figures(item)


def test_localities_load_through_contract_models():
    data = load("localities.json")
    districts = [District.model_validate(x) for x in data["districts"]]
    blocks = [Block.model_validate(x) for x in data["blocks"]]
    villages = [Village.model_validate(x) for x in data["villages"]]
    assert {d.code for d in districts} >= {b.district_code for b in blocks}
    assert {b.code for b in blocks} >= {v.block_code for v in villages}
    assert len(villages) >= 3
    assert "Lasalgaon" in {v.name for v in villages}
    assert all(v.households > 0 for v in villages)


def test_archetypes_load_with_bounds_and_eligibility():
    archetypes = [ArchetypeSummary.model_validate(x) for x in load("archetypes.json")]
    assert {a.id for a in archetypes} == {"dairy", "onion_cultivation", "poultry", "tailoring", "kirana", "flour_mill"}
    for a in archetypes:
        assert a.unit_scale_min <= a.unit_scale_default <= a.unit_scale_max, a.id
        assert a.eligibility_fields, a.id


def test_schemes_load_and_are_marked_illustrative():
    schemes = [SchemeSummary.model_validate(x) for x in load("schemes.json")]
    assert len(schemes) == 6
    for s in schemes:
        assert s.interest_rate_min <= s.interest_rate_max, s.id
        assert s.verified_on == "1970-01-01", s.id


def test_stage_events_run_then_finish_for_all_six_stages():
    events = [StageEvent.model_validate(x) for x in load("stage_events.json")]
    expected = ["intake", "market", "cost", "schemes", "dpr", "explanation"]
    assert [e.stage for e in events] == [s for s in expected for _ in range(2)]
    for running, done in zip(events[::2], events[1::2]):
        assert running.status == "running"
        assert done.status == "done"
        assert done.duration_ms is not None and done.sources, done.stage


def test_report_is_the_demo_persona(report):
    assert report.status == "done"
    assert report.input.archetype_id == "dairy"
    assert report.input.own_contribution == 100000
    assert report.input.eligibility.gender == "female"
    assert report.input.eligibility.social_category == "obc"
    assert report.input.eligibility.education == "10th_pass"
    assert report.input.language == "mr"
    assert report.engine.archetype_id == "dairy"
    assert report.explanation.language == "mr"


def test_placeholders_all_resolve_against_engine_figures(report):
    registry = report.engine.figures
    for text in explanation_texts(report):
        for figure_id in PLACEHOLDER.findall(text):
            assert figure_id in registry, figure_id


def test_no_raw_digits_outside_placeholders(report):
    titles = [s.title for s in report.explanation.sections]
    for text in explanation_texts(report) + titles:
        assert not DIGIT.search(PLACEHOLDER.sub("", text)), text


def test_verified_and_total_match_placeholder_count(report):
    count = sum(len(PLACEHOLDER.findall(t)) for t in explanation_texts(report))
    assert report.explanation.verified == count
    assert report.explanation.total == count
    assert count > 0


def test_every_nested_figure_is_in_the_registry(report):
    registry = report.engine.figures
    dumped = report.engine.model_dump(exclude={"figures"})
    seen = list(nested_figures(dumped))
    assert seen
    for figure in seen:
        assert figure["id"] in registry, figure["id"]
        assert registry[figure["id"]].value == figure["value"], figure["id"]


def test_emi_matches_closed_form_and_schedule_closes_at_zero(report):
    terms = report.engine.schemes.best.terms
    principal = terms.principal
    r = terms.interest_rate / 12 / 100
    n = terms.tenure_months - terms.moratorium_months
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    assert terms.emi == round(emi)

    rows = report.engine.repayment
    assert len(rows) == terms.tenure_months
    assert rows[-1].closing == 0
    assert sum(row.principal for row in rows) == principal
    assert sum(row.interest for row in rows) == terms.total_interest
    assert all(row.opening - row.principal == row.closing for row in rows)
    assert all(row.closing >= 0 for row in rows)


def test_figures_add_up(report):
    engine = report.engine
    figs = engine.figures
    cost_items = sum(item.figure.value for item in engine.cost.items)
    assert cost_items + figs["working_capital"].value == engine.cost.project_cost.value
    assert engine.finance.funding_gap.value == engine.cost.project_cost.value - engine.finance.own_contribution.value
    assert engine.finance.loan.value == engine.finance.funding_gap.value
    assert figs["emi"].value == engine.schemes.best.terms.emi
    assert figs["min_dscr"].value == min(p.dscr for p in engine.projections if p.dscr is not None)


def test_archetype_eligibility_fields_are_real_intake_fields():
    eligibility_fields = set(Eligibility.model_fields)
    for a in (ArchetypeSummary.model_validate(x) for x in load("archetypes.json")):
        assert set(a.eligibility_fields) <= eligibility_fields, a.id


def test_demo_village_is_in_the_localities_fixture(report):
    codes = {v["code"] for v in load("localities.json")["villages"]}
    assert report.input.village_code in codes
    assert report.engine.village_code == report.input.village_code


def test_scheme_urls_and_dates_are_marked_fixture_data():
    # Rule 6: only the PMEGP URL comes from docs/trd.md; everything else is a placeholder.
    for s in (SchemeSummary.model_validate(x) for x in load("schemes.json")):
        if s.id == "pmegp":
            assert s.source_url == "https://www.kviconline.gov.in/pmegpeportal/"
        else:
            assert s.source_url.startswith("https://example.invalid/"), s.id


def test_verdict_and_scheme_tell_one_story(report):
    engine = report.engine
    best = engine.schemes.best
    assert best.scheme_id == "mudra" and best.tier == "kishore"
    assert 50000 < best.terms.principal <= 500000  # MUDRA Kishore band
    dscr_signal = next(s for s in engine.verdict.signals if s.name == "dscr")
    assert (dscr_signal.level == "feasible") == (engine.min_dscr.value >= 1.5)
    assert engine.verdict.level == "feasible"
    assert engine.path_to_yes is None
