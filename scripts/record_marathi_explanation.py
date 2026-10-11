"""One-shot record script for AC 4: explain_report in Marathi (LLM_MODE=record).

Run manually with real Gemini credentials:

    LLM_MODE=record LLM_PRIMARY=gemini GEMINI_API_KEY=<key> \
        .venv/bin/python scripts/record_marathi_explanation.py

The script commits the resulting cache file path to stdout.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.contracts import EngineResult
from llm.explain import explain_report

FIXTURE = ROOT / "fixtures" / "report.json"


def main() -> None:
    mode = os.getenv("LLM_MODE", "replay")
    if mode != "record":
        print(f"ERROR: LLM_MODE must be 'record', got '{mode}'", file=sys.stderr)
        sys.exit(1)

    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    engine = EngineResult.model_validate(data["engine"])

    print("Calling Gemini (LLM_MODE=record) for Marathi Entrepreneur View …")
    result = explain_report(engine, "mr")

    if not result.available:
        print("ERROR: LLM call failed — no cache file written.", file=sys.stderr)
        sys.exit(1)

    cache_dir = ROOT / "data" / "llm_cache"
    files = sorted(cache_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    newest = files[0] if files else None

    print(f"✓ explain_report returned available=True, verified={result.verified}/{result.total}")
    print(f"  sections: {[s.key for s in result.sections]}")
    if newest:
        print(f"  cache file written: data/llm_cache/{newest.name}")
        print(f"\nCommit with:\n  git add data/llm_cache/{newest.name}")
    else:
        print("  WARNING: no cache file found in data/llm_cache/")


if __name__ == "__main__":
    main()
