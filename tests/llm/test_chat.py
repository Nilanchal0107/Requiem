"""Ticket 40: a what-if question gets a suggested change and sim figures; the reply passes verify; the report is untouched."""
import json
from pathlib import Path
from types import SimpleNamespace

from api.contracts import Change, IntakeInput, Report
from engine import run_engine
from llm import chat as chat_mod
from llm.retrieval import SchemeIndex
from llm.verifier import verify

ROOT = Path(__file__).resolve().parents[2]


def _load(rel):
    return json.loads((ROOT / rel).read_text())


ARCH = _load("data/archetypes/dairy.json")
SCHEMES = [_load(f"data/schemes/{s}.json") for s in ("mudra", "pmegp", "standup_india")]
VILLAGE = {**_load("data/census/niphad_villages.json")[0], "osm_counts": {}}
INPUT = IntakeInput(
    village_code=VILLAGE["code"], archetype_id="dairy", unit_scale=5, own_contribution=100000,
    eligibility={"age": 30, "gender": "female", "social_category": "obc", "education": "10th_pass"},
)


def _what_if(changes: list[Change]):
    update = {c.field: c.to_value for c in changes}
    return run_engine(INPUT.model_copy(update=update), ARCH, SCHEMES, VILLAGE, current_year=2026, with_path_to_yes=False)


def _completion(content=None, calls=None):
    tool_calls = [SimpleNamespace(id=f"c{i}", function=SimpleNamespace(name=n, arguments=json.dumps(a)))
                  for i, (n, a) in enumerate(calls or [])] or None
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content, tool_calls=tool_calls))])


def test_what_if_returns_suggested_change_and_verified_reply(monkeypatch):
    engine = run_engine(INPUT, ARCH, SCHEMES, VILLAGE, current_year=2026)
    report = Report(id="r1", status="done", input=INPUT, engine=engine, explanation=None,
                    created_at="2026-01-01T00:00:00", owner_id=None)
    before = report.model_dump()
    replies = iter([
        _completion(calls=[("get_dpr", {"section": "verdict"}), ("simulate", {"changes": [{"field": "unit_scale", "to_value": 3}]})]),
        _completion("With fewer animals your lowest repayment cover becomes {{sim.min_dscr}}. It was 5 before."),
    ])
    monkeypatch.setattr(chat_mod, "complete", lambda *a, **k: next(replies))
    urls = {s["id"]: s["source_url"] for s in SCHEMES}
    index = SchemeIndex(ROOT / "data" / "scheme_texts", urls)

    res = chat_mod.chat(report, "what if I start with 3 animals?", [], "en", index=index, what_if=_what_if)

    assert res.tools_used == ["get_dpr", "simulate"]
    assert [(c.field, c.from_value, c.to_value) for c in res.suggested_changes] == [("unit_scale", 5.0, 3.0)]
    assert "sim.min_dscr" in res.figures
    assert verify(res.reply, {**engine.figures, **res.figures}).offending == []
    assert "{{sim.min_dscr}}" in res.reply and "5" not in res.reply  # digit sentence was stripped
    assert report.model_dump() == before


def test_get_dpr_masks_figure_values():
    engine = run_engine(INPUT, ARCH, SCHEMES, VILLAGE, current_year=2026)
    out = chat_mod.tool_get_dpr(engine, "market")
    assert "value" not in json.dumps(out) and "{{demand}}" in json.dumps(out)
