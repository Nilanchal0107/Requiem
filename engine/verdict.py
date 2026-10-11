"""Verdict from DSCR, market gap, payback and Scheme match (TRD §5.7). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import Figure, MarketAnalysis, SchemeMatch, Verdict


LEVEL_RANK: dict[str, int] = {
    "feasible": 1,
    "feasible_with_changes": 2,
    "not_feasible": 3,
}
RANK_TO_LEVEL: dict[int, str] = {
    1: "feasible",
    2: "feasible_with_changes",
    3: "not_feasible",
}


def decide_verdict(
    archetype: dict[str, Any],
    market: MarketAnalysis,
    min_dscr: Figure,
    payback: Figure,
    schemes: SchemeMatch,
    revolving: bool = False,
) -> Verdict:
    """Four signals (dscr, market_gap, payback, scheme) and the worst level (TRD §5.7).

    market_gap signal is skipped in aggregator mode. Payback is compared with the best Scheme's tenure.
    V2 must add at least one assert check.
    """
    assert isinstance(archetype, dict)
    assert isinstance(market, MarketAnalysis)
    assert isinstance(min_dscr, Figure)
    assert isinstance(payback, Figure)
    assert isinstance(schemes, SchemeMatch)

    from api.contracts import VerdictSignal

    signals: list[VerdictSignal] = []

    # 1. DSCR signal: >= 1.5 -> feasible, >= 1.25 -> feasible_with_changes, < 1.25 -> not_feasible
    dscr_val = min_dscr.value
    if dscr_val >= 1.5:
        dscr_lvl = "feasible"
    elif dscr_val >= 1.25:
        dscr_lvl = "feasible_with_changes"
    else:
        dscr_lvl = "not_feasible"
    signals.append(VerdictSignal(name="dscr", level=dscr_lvl, figure_id=min_dscr.id))

    # 2. Market Gap signal (local mode only)
    # feasible: gap > 10% of demand; feasible_with_changes: within ±10% of demand; not_feasible: gap < -10% of demand
    mode = archetype.get("market", {}).get("mode", "local")
    if mode != "aggregator":
        demand_val = market.demand.value
        gap_val = market.market_gap.value
        threshold = 0.10 * demand_val
        if gap_val > threshold:
            mg_lvl = "feasible"
        elif gap_val >= -threshold:
            mg_lvl = "feasible_with_changes"
        else:
            mg_lvl = "not_feasible"
        signals.append(VerdictSignal(name="market_gap", level=mg_lvl, figure_id=market.market_gap.id))

    # 3. Payback signal: <= loan tenure -> feasible; <= tenure + 12 months -> feasible_with_changes; longer -> not_feasible
    tenure = schemes.best.terms.tenure_months if schemes.best and not revolving else 60
    pb_val = payback.value
    if pb_val <= tenure:
        pb_lvl = "feasible"
    elif pb_val <= tenure + 12:
        pb_lvl = "feasible_with_changes"
    else:
        pb_lvl = "not_feasible"
    signals.append(VerdictSignal(name="payback", level=pb_lvl, figure_id=payback.id))

    # 4. Scheme signal: best exists -> feasible; else not_feasible
    if schemes.best is not None:
        sc_lvl = "feasible"
    else:
        sc_lvl = "not_feasible"
    signals.append(VerdictSignal(name="scheme", level=sc_lvl, figure_id=None))

    worst_rank = max(LEVEL_RANK[s.level] for s in signals)
    overall_level = RANK_TO_LEVEL[worst_rank]

    return Verdict(level=overall_level, signals=signals)

