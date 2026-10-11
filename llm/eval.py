"""Eval: `uv run python -m llm.eval` prints scheme-match accuracy and verifier pass rate (TRD §6.7)."""
from typing import Any


def run_eval(
    cases: list[dict[str, Any]],
    *,
    archetypes: list[dict[str, Any]],
    schemes: list[dict[str, Any]],
    villages: dict[str, dict[str, Any]],
    current_year: int,
) -> dict[str, float]:
    """Run each case through the engine and the Entrepreneur View (TRD §6.7). Returns {"scheme_match": x, "verifier_pass": y}.

    Catalogue and village rows come in as arguments, so eval does not import `data`. V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.eval.run_eval")


def main() -> None:
    """Entry point for `python -m llm.eval` (TRD §6.7). Wiring of the catalogue and village rows is open; see the ticket comment.

    V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.eval.main")


if __name__ == "__main__":
    main()
