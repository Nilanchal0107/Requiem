"""Chat advisor tool loop (TRD §6.5, §4.4). Never writes to the DB."""
import json
import logging
from pathlib import Path
from typing import Any, Callable

from api.contracts import (
    ChatResponse,
    ChatTurn,
    Change,
    Citation,
    EngineResult,
    Figure,
    Language,
    Report,
)
from llm.client import complete
from llm.retrieval import SchemeIndex
from llm.verifier import verify

log = logging.getLogger(__name__)

# Injected by api/: runs run_engine with the changes applied. Keeps llm off the catalogue and the DB.
WhatIf = Callable[[list[Change]], EngineResult]

_PROMPT = Path(__file__).resolve().parent / "prompts" / "chat_system.md"
_LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "mr": "Marathi"}
_SECTIONS = ["market", "cost", "finance", "schemes", "repayment", "projections", "verdict", "path_to_yes",
             "break_even_month", "payback_months", "min_dscr"]
_MAX_ROUNDS = 3
_HISTORY_TURNS = 10

_TOOLS = [
    {"type": "function", "function": {
        "name": "get_dpr", "description": "Read one section of the report.",
        "parameters": {"type": "object", "properties": {"section": {"type": "string", "enum": _SECTIONS}},
                       "required": ["section"]}}},
    {"type": "function", "function": {
        "name": "search_schemes", "description": "Search Scheme rules; the query must be in English.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "simulate", "description": "Re-run the engine with changes applied.",
        "parameters": {"type": "object", "properties": {"changes": {"type": "array", "items": {
            "type": "object",
            "properties": {"field": {"type": "string", "enum": ["own_contribution", "unit_scale", "tenure_months"]},
                           "to_value": {"type": "number"}},
            "required": ["field", "to_value"]}}}, "required": ["changes"]}}},
]


def _mask_figures(node: Any) -> Any:
    """Replace each Figure dict by its placeholder and label: the model never sees a value."""
    if isinstance(node, dict):
        if {"id", "label", "value", "unit", "source"} <= node.keys():
            return {"placeholder": "{{" + node["id"] + "}}", "label": node["label"], "unit": node["unit"]}
        return {k: _mask_figures(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_mask_figures(v) for v in node]
    return node


def chat(
    report: Report,
    message: str,
    history: list[ChatTurn],
    language: Language,
    *,
    index: SchemeIndex,
    what_if: WhatIf,
) -> ChatResponse:
    """Tool loop (TRD §6.5, §4.4) of at most 3 rounds over get_dpr, search_schemes and simulate, then the verifier on the reply.

    Simulate figures get the `sim.` prefix in `ChatResponse.figures`. Each simulate result becomes a
    `suggested_changes` entry. A later simulate replaces the `sim.` figures of an earlier one.
    """
    assert report.engine is not None, "chat needs a finished report"
    assert message.strip(), "message must not be empty"
    engine = report.engine

    system = _PROMPT.read_text(encoding="utf-8")
    for token, value in {
        "{language_name}": _LANGUAGE_NAMES[language],
        "{sections}": ", ".join(_SECTIONS),
        "{archetype_id}": engine.archetype_id,
        "{verdict_level}": engine.verdict.level,
        "{figure_table}": "\n".join(f"  {{{{{fid}}}}}  ->  {f.label} [{f.unit}]" for fid, f in engine.figures.items()),
    }.items():
        system = system.replace(token, value)
    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    messages += [{"role": t.role, "content": t.content} for t in history[-_HISTORY_TURNS:]]
    messages.append({"role": "user", "content": message})

    tools_used: list[str] = []
    citations: list[Citation] = []
    sim_figures: dict[str, Figure] = {}
    suggested: list[Change] = []
    reply = ""

    for round_no in range(_MAX_ROUNDS + 1):
        # the last pass offers no tools, so the loop always ends in text
        resp = complete(messages, tools=_TOOLS if round_no < _MAX_ROUNDS else None, temperature=0.3)
        msg = resp.choices[0].message
        calls = getattr(msg, "tool_calls", None)
        if not calls:
            reply = (msg.content or "").strip()
            break
        messages.append({
            "role": "assistant", "content": msg.content or "",
            "tool_calls": [{"id": c.id, "type": "function",
                            "function": {"name": c.function.name, "arguments": c.function.arguments}} for c in calls],
        })
        for c in calls:
            try:
                args = json.loads(c.function.arguments or "{}")
                result = _run_tool(c.function.name, args, report, index, what_if, citations, sim_figures, suggested)
                if c.function.name not in tools_used:
                    tools_used.append(c.function.name)
            except Exception as exc:  # noqa: BLE001 - tell the model, let it recover
                log.warning("chat: tool %s failed: %s", c.function.name, exc)
                result = {"error": str(exc)}
            messages.append({"role": "tool", "tool_call_id": c.id, "content": json.dumps(result, ensure_ascii=False)})

    figures = {**engine.figures, **sim_figures}
    bad = set(verify(reply, figures).offending)
    if bad:  # no regeneration for chat: drop the failing sentences
        from llm.verifier import _split_sentences

        reply = " ".join(s for s in _split_sentences(reply) if s not in bad)
    return ChatResponse(
        reply=reply, figures=sim_figures, citations=citations, suggested_changes=suggested, tools_used=tools_used,
    )


def _current_value(report: Report, field: str) -> float:
    inp, best = report.input, report.engine.schemes.best  # type: ignore[union-attr]
    if field == "tenure_months":
        return float(inp.tenure_months or (best.terms.tenure_months if best else 0))
    return float(getattr(inp, field))


def _run_tool(
    name: str,
    args: dict[str, Any],
    report: Report,
    index: SchemeIndex,
    what_if: WhatIf,
    citations: list[Citation],
    sim_figures: dict[str, Figure],
    suggested: list[Change],
) -> dict[str, Any]:
    """Run one tool call. Appends to the accumulators; returns what the model gets to read."""
    engine = report.engine
    assert engine is not None
    if name == "get_dpr":
        return tool_get_dpr(engine, args["section"])
    if name == "search_schemes":
        hits = index.search(args["query"])
        citations.extend(h for h in hits if h not in citations)
        return {"passages": [{"scheme_id": h.scheme_id, "text": h.snippet} for h in hits]}
    assert name == "simulate", f"unknown tool {name}"
    changes = [
        Change(field=c["field"], from_value=_current_value(report, c["field"]), to_value=c["to_value"],
               resulting_verdict=engine.verdict.level)  # placeholder, set from the result below
        for c in args["changes"]
    ]
    assert changes, "simulate needs at least one change"
    result = tool_simulate(what_if, changes)
    suggested.extend(c.model_copy(update={"resulting_verdict": result.verdict.level}) for c in changes)
    sim_figures.clear()
    for fid, fig in result.figures.items():
        sim_figures[f"sim.{fid}"] = fig.model_copy(update={"id": f"sim.{fid}"})
    return {
        "verdict": result.verdict.level,
        "signals": {s.name: s.level for s in result.verdict.signals},
        "figures": [{"placeholder": "{{" + k + "}}", "label": f.label, "unit": f.unit} for k, f in sim_figures.items()],
    }


def tool_get_dpr(engine: EngineResult, section: str) -> dict[str, Any]:
    """Return one part of the stored EngineResult (TRD §6.5; e.g. market, cost, schemes, finance, verdict).

    Figure values are masked to placeholders, so the model never reads a number.
    """
    assert section in _SECTIONS, f"unknown section {section!r}; choose from {_SECTIONS}"
    return {section: _mask_figures(engine.model_dump(mode="json")[section])}


def tool_simulate(what_if: WhatIf, changes: list[Change]) -> EngineResult:
    """Run the what-if with `changes` applied (TRD §6.5, simulate tool). The caller reads `.verdict` for `resulting_verdict`."""
    assert changes, "changes must not be empty"
    return what_if(changes)
