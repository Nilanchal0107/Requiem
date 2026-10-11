"""Checks the engine declarations (ticket 06): imports stay pure, every TRD §5 function has a home, wiring stops at the first stub."""
import importlib
import subprocess
import sys
import typing
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

DECLARED = {
    "engine.market": ["households_now", "our_capacity", "sales_ceiling", "analyse_market"],
    "engine.cost": ["build_cost"],
    "engine.schemes": ["match_schemes"],
    "engine.finance": [
        "build_loan_terms",
        "repayment_schedule",
        "monthly_operating",
        "project_years",
        "build_means_of_finance",
        "break_even_month",
        "payback_months",
        "min_dscr",
    ],
    "engine.verdict": ["decide_verdict"],
    "engine.path_to_yes": ["find_path_to_yes"],
    "engine.figures": ["FigureRegistry"],
    "engine": ["run_engine"],
}

FORBIDDEN = ["llm", "data", "sqlmodel", "openai", "httpx", "fastapi"]


def test_importing_engine_pulls_in_no_io_or_llm_packages():
    # A fresh interpreter, so modules imported by other tests don't leak into sys.modules.
    code = (
        "import sys, engine, engine.cost, engine.finance, engine.figures, engine.market, "
        "engine.path_to_yes, engine.schemes, engine.verdict\n"
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
        hints = typing.get_type_hints(obj if not isinstance(obj, type) else obj.__init__)
        assert "return" in hints or isinstance(obj, type), f"{module}.{name} has no return type"


@pytest.mark.skip(reason="V1 declaration test superceded by V2 implementation")
def test_run_engine_stops_at_the_first_stub():
    from engine import run_engine

    with pytest.raises(NotImplementedError):
        run_engine(None, {}, [], {}, current_year=2026)

