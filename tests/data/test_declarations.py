"""Checks the data declarations (ticket 08): clean imports, scheme validation, declared loader signatures, placeholder folders."""
import inspect
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]

FOLDERS = ["archetypes", "schemes", "scheme_texts", "census", "osm", "llm_cache"]

VALID_SCHEME = {
    "id": "pmegp",
    "name": "PMEGP",
    "covers": "New manufacturing and service units",
    "sectors": ["allied", "service"],
    "source_url": "https://www.kviconline.gov.in/pmegpeportal/",
    "verified_on": "2026-10-11",
    "rules": [],
    "own_contribution_pct": [{"pct": 10}],
    "loan": {
        "max": 4750000,
        "interest_rate": 10.0,
        "rate_source": "assumption",
        "max_tenure_months": 84,
        "moratorium_months": 6,
        "moratorium_mode": "serviced",
        "repayment_mode": "emi",
    },
    "tiers": [],
    "subsidy": {"type": "capital_backended", "lock_in_months": 36, "rates": [{"pct": 15}]},
}


def test_importing_data_pulls_in_no_engine_or_llm():
    # A fresh interpreter, so modules imported by other tests don't leak into sys.modules.
    code = (
        "import sys, data, data.models, data.loaders\n"
        "bad = [m for m in sys.modules if m.split('.')[0] in ('engine', 'llm')]\n"
        "print(bad)\n"
        "raise SystemExit(1 if bad else 0)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_scheme_accepts_a_complete_item():
    from data.models import Scheme

    assert Scheme(**VALID_SCHEME).source_url.startswith("https://")


@pytest.mark.parametrize("missing", ["source_url", "verified_on"])
def test_scheme_rejects_an_item_without_source_or_verified_date(missing):
    from data.models import Scheme

    item = {k: v for k, v in VALID_SCHEME.items() if k != missing}
    with pytest.raises(ValidationError):
        Scheme(**item)


@pytest.mark.parametrize("bad_url", ["", "   ", "TBD"])
def test_scheme_rejects_a_blank_or_non_url_source(bad_url):
    from data.models import Scheme

    with pytest.raises(ValidationError):
        Scheme(**{**VALID_SCHEME, "source_url": bad_url})


def test_typo_in_a_key_is_rejected():
    from data.models import Condition

    with pytest.raises(ValidationError):
        Condition(field="x", op="eq", value=1, whn=[])


@pytest.mark.parametrize("name", ["load_archetypes", "load_schemes", "load_scheme_texts", "seed_villages"])
def test_loaders_and_seed_are_declared_and_not_implemented(name):
    import data.loaders as loaders

    fn = getattr(loaders, name)
    assert fn.__doc__, f"data.loaders.{name} has no docstring"
    assert inspect.signature(fn).return_annotation is not inspect.Signature.empty
    with pytest.raises(NotImplementedError):
        fn(*([None] if name == "seed_villages" else []))


@pytest.mark.parametrize("folder", FOLDERS)
def test_folders_exist_with_only_a_placeholder(folder):
    path = ROOT / "data" / folder
    assert (path / ".gitkeep").is_file(), f"data/{folder}/.gitkeep is missing"
    assert not any(p.suffix == ".json" for p in path.iterdir()), f"data/{folder} holds catalogue content"
