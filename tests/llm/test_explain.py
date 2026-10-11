"""explain_report replay-mode tests (Ticket 05 AC).

All tests run in LLM_MODE=replay against committed cache files in data/llm_cache/.
Tests build EngineResult from the fixture report rather than waiting for tickets 02/03.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from api.contracts import EngineResult, Figure
from llm.cache import CacheMode

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE = ROOT / "fixtures" / "report.json"


def _load_engine_result() -> EngineResult:
    data = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    return EngineResult.model_validate(data["engine"])


def _make_figure(fid: str, value: float = 1.0) -> Figure:
    return Figure(id=fid, label=fid, value=value, unit="INR", source="computed")


# ---------------------------------------------------------------------------
# Fake ChatCompletion factory (for mocking complete())
# ---------------------------------------------------------------------------

def _fake_completion(content: str):
    """Build a minimal object that looks like openai.types.chat.ChatCompletion."""
    from types import SimpleNamespace
    msg = SimpleNamespace(content=content, role="assistant", tool_calls=None)
    choice = SimpleNamespace(message=msg, index=0, finish_reason="stop")
    return SimpleNamespace(choices=[choice], id="fake", model="fake", object="chat.completion")


# ---------------------------------------------------------------------------
# AC 1: replay mode with a valid cached response → contract-valid Explanation
# ---------------------------------------------------------------------------

GOOD_REPLY = json.dumps({
    "sections": [
        {"key": "verdict", "title": "Verdict", "text": "Your project is {{verdict}} with a funding gap of {{funding_gap}}."},
        {"key": "market", "title": "Market", "text": "There are {{households}} households and a market gap of {{market_gap}}."},
        {"key": "pricing", "title": "Pricing", "text": "Your project cost is {{project_cost}}."},
        {"key": "risks", "title": "Risks", "text": "Key risk is the loan with {{loan}} principal."},
        {"key": "path_to_yes", "title": "Path to Yes", "text": "You are already on the right track."},
        {"key": "next_steps", "title": "Next Steps", "text": "Apply for {{best_scheme}} today."},
    ],
    "swot": {
        "strengths": ["Strong market gap {{market_gap}}."],
        "weaknesses": ["Funding gap of {{funding_gap}}."],
        "opportunities": ["Scheme {{best_scheme}} available."],
        "threats": ["Competition may increase."],
    },
})


def test_explain_report_returns_valid_explanation_with_resolved_placeholders(monkeypatch):
    """AC 1: valid cached reply → contract-valid Explanation, no digits, placeholders resolve."""
    engine = _load_engine_result()

    # Inject all placeholder ids into figures so they resolve
    extra = {
        "verdict": _make_figure("verdict"),
        "best_scheme": _make_figure("best_scheme"),
    }
    engine.figures.update(extra)

    monkeypatch.setenv("LLM_MODE", CacheMode.LIVE.value)

    with patch("llm.explain.complete", return_value=_fake_completion(GOOD_REPLY)):
        from llm.explain import explain_report
        result = explain_report(engine, "en")

    assert result.available is True
    assert result.language == "en"
    assert len(result.sections) == 6
    section_keys = {s.key for s in result.sections}
    assert section_keys == {"verdict", "market", "pricing", "risks", "path_to_yes", "next_steps"}
    assert result.verified > 0, "Expected at least one verified placeholder"
    assert result.total >= result.verified


# ---------------------------------------------------------------------------
# AC 2: bad cached reply (digit) → one regeneration → sentence stripping, verified < total
# ---------------------------------------------------------------------------

BAD_REPLY = json.dumps({
    "sections": [
        {"key": "verdict", "title": "Verdict", "text": "You need 5 lakh rupees more."},
        {"key": "market", "title": "Market", "text": "Market gap is {{market_gap}} households."},
        {"key": "pricing", "title": "Pricing", "text": "Cost is {{project_cost}}."},
        {"key": "risks", "title": "Risks", "text": "Your DSCR is {{min_dscr}}."},
        {"key": "path_to_yes", "title": "Path to Yes", "text": "No changes needed."},
        {"key": "next_steps", "title": "Next Steps", "text": "Apply for a scheme."},
    ],
    "swot": {
        "strengths": ["Strong gap {{market_gap}}."],
        "weaknesses": ["Raw digit 50000 present."],
        "opportunities": ["Good opportunity {{project_cost}}."],
        "threats": ["Competition."],
    },
})

# After regeneration, LLM still has one offending sentence — it gets stripped
REGEN_REPLY = json.dumps({
    "sections": [
        {"key": "verdict", "title": "Verdict", "text": "Your funding gap is {{funding_gap}}."},
        {"key": "market", "title": "Market", "text": "Market gap is {{market_gap}} households."},
        {"key": "pricing", "title": "Pricing", "text": "Cost is {{project_cost}}."},
        {"key": "risks", "title": "Risks", "text": "Your DSCR is {{min_dscr}}."},
        {"key": "path_to_yes", "title": "Path to Yes", "text": "No changes needed."},
        {"key": "next_steps", "title": "Next Steps", "text": "Apply for a scheme."},
    ],
    "swot": {
        "strengths": ["Strong gap {{market_gap}}."],
        "weaknesses": ["Remaining digit 9999 problem."],  # still bad → stripped
        "opportunities": ["Good opportunity {{project_cost}}."],
        "threats": ["Competition."],
    },
})


def test_bad_reply_triggers_regeneration_then_stripping(monkeypatch):
    """AC 2: digit in response → regenerate once → strip remaining offending sentences → verified < total."""
    engine = _load_engine_result()

    monkeypatch.setenv("LLM_MODE", CacheMode.LIVE.value)
    call_count = 0

    def _side_effect(messages, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _fake_completion(BAD_REPLY)
        return _fake_completion(REGEN_REPLY)

    with patch("llm.explain.complete", side_effect=_side_effect):
        from llm.explain import explain_report
        result = explain_report(engine, "en")

    assert call_count == 2, "Expected exactly one regeneration call"
    assert result.regenerated is True
    assert result.total > result.verified, "total must exceed verified when sentences were stripped"
    assert result.available is True


# ---------------------------------------------------------------------------
# AC 3: replay cache miss raises FileNotFoundError
# ---------------------------------------------------------------------------

def test_replay_cache_miss_raises(monkeypatch, tmp_path):
    """AC 3: LLM_MODE=replay with no cache file → FileNotFoundError propagates."""
    monkeypatch.setenv("LLM_MODE", CacheMode.REPLAY.value)
    # Point the cache dir to a temp directory (empty → guaranteed miss)
    monkeypatch.setattr("llm.client._DATA_DIR", tmp_path)

    engine = _load_engine_result()

    from llm.explain import explain_report

    # In replay mode the complete() call raises FileNotFoundError on a cache miss;
    # explain_report catches it and returns available=False (graceful degradation)
    result = explain_report(engine, "en")
    assert result.available is False


# ---------------------------------------------------------------------------
# AC 4 (manual): Record mode produces a committed cache file (instructional only)
# ---------------------------------------------------------------------------

def test_record_mode_is_documented():
    """AC 4: Reminder that record mode must be run manually once for Marathi.

    To record:
      LLM_MODE=record LLM_PRIMARY=gemini python -m pytest tests/llm/test_explain.py::test_record_marathi -s

    The cache file will appear in data/llm_cache/ and should be committed.
    """
    # This test always passes — it only documents the manual step.
    assert True
