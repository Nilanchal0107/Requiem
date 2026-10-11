"""Scheme matching, eligibility, unlock hints and ranking (TRD §5.4). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import IntakeInput, SchemeMatch


def match_schemes(
    input: IntakeInput,
    archetype: dict[str, Any],
    schemes: list[dict[str, Any]],
    project_cost: int,
) -> SchemeMatch:
    """Evaluate rules and the Own Contribution check, size the loan, rank by effective_rate (TRD §5.4).

    Loan terms come from `finance.build_loan_terms`. Returns best, alternatives and ineligible with unlock hints.
    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.schemes.match_schemes")
