"""Checks the LLM declarations (ticket 07): imports stay clear of the DB and API internals, every TRD §6 function has a home, prompts exist."""
import importlib
import subprocess
import sys
import typing
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

DECLARED = {
    "llm.client": ["complete", "complete_json"],
    "llm.cache": ["cache_key"],
    "llm.explain": ["explain_report", "explain_comparison"],
    "llm.verifier": ["verify"],
    "llm.intake": ["parse_intake", "missing_fields"],
    "llm.retrieval": ["SchemeIndex"],
    "llm.chat": ["chat", "tool_get_dpr", "tool_simulate"],
    "llm.eval": ["run_eval", "main"],
}

PROMPTS = ["entrepreneur_view.md", "comparison.md", "intake_parse.md", "chat_system.md"]

# llm may import api.contracts, engine and the openai SDK. Never the DB, catalogue loader or API internals.
FORBIDDEN = ["data", "sqlmodel"]


def test_importing_llm_pulls_in_no_db_or_api_internals():
    # A fresh interpreter, so modules imported by other tests don't leak into sys.modules.
    code = (
        "import sys, llm, llm.client, llm.cache, llm.explain, llm.verifier, llm.intake, "
        "llm.retrieval, llm.chat, llm.eval\n"
        f"bad = [m for m in sys.modules if m.split('.')[0] in {FORBIDDEN!r}]\n"
        "bad += [m for m in sys.modules if m.startswith('api.') and m != 'api.contracts']\n"
        "print(bad)\n"
        "raise SystemExit(1 if bad else 0)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("module, names", DECLARED.items())
def test_every_trd_function_has_a_declared_home(module, names):
    mod = importlib.import_module(module)
    for name in names:
        obj = getattr(mod, name, None)
        assert callable(obj), f"{module}.{name} is not declared"
        assert obj.__doc__, f"{module}.{name} has no docstring"
        if not isinstance(obj, type):
            hints = typing.get_type_hints(obj)
            assert "return" in hints, f"{module}.{name} has no return type"


def test_cache_modes_are_a_closed_set():
    from llm.cache import CacheMode

    assert [m.value for m in CacheMode] == ["live", "record", "replay"]


@pytest.mark.parametrize("name", PROMPTS)
def test_one_prompt_file_per_use(name):
    assert (ROOT / "llm" / "prompts" / name).is_file(), f"llm/prompts/{name} is missing"
