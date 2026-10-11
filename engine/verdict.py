"""Verdict from DSCR, market gap, payback and Scheme match (TRD §5.7). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import Figure, MarketAnalysis, SchemeMatch, Verdict


def decide_verdict(
    archetype: dict[str, Any],
    market: MarketAnalysis,
    min_dscr: Figure,
    payback: Figure,
    schemes: SchemeMatch,
) -> Verdict:
    """Four signals (dscr, market_gap, payback, scheme) and the worst level (TRD §5.7).

    market_gap signal is skipped in aggregator mode. Payback is compared with the best Scheme's tenure.
    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.verdict.decide_verdict")
