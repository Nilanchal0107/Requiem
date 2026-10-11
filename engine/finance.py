"""Loan, repayment, projections, DSCR, break-even and payback (TRD §5.5–5.6). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import (
    CostBreakdown,
    Figure,
    IntakeInput,
    LoanTerms,
    MarketAnalysis,
    MeansOfFinance,
    RepaymentRow,
    SchemeOption,
    YearProjection,
)
from engine.figures import FigureRegistry

HORIZON_MONTHS = 60
NOT_PAID_BACK = 999           # payback_months when not reached within HORIZON_MONTHS


def build_loan_terms(principal: int, scheme: dict[str, Any], tenure_months: int | None) -> LoanTerms:
    """EMI, total interest and moratorium mode for `principal` (TRD §5.5). None tenure = Scheme default.

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.finance.build_loan_terms")


def repayment_schedule(terms: LoanTerms, scheme: dict[str, Any], subsidy: int) -> list[RepaymentRow]:
    """Month-by-month schedule closing at exactly 0, with PMEGP back-ended subsidy applied at lock-in (TRD §5.5).

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.finance.repayment_schedule")


def monthly_operating(
    input: IntakeInput,
    archetype: dict[str, Any],
    market: MarketAnalysis,
) -> list[tuple[int, int]]:
    """(revenue, operating_cost) for each of the 60 months (TRD §5.3).

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.finance.monthly_operating")


def project_years(
    input: IntakeInput,
    archetype: dict[str, Any],
    market: MarketAnalysis,
    cost: CostBreakdown,
    schedule: list[RepaymentRow],
) -> list[YearProjection]:
    """Five yearly rows: revenue, opex, depreciation, interest, net profit, cash flow, DSCR (TRD §5.6).

    Tax is ignored (assumption). V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.finance.project_years")


def build_means_of_finance(
    input: IntakeInput,
    cost: CostBreakdown,
    best: SchemeOption | None,
    reg: FigureRegistry,
) -> MeansOfFinance:
    """Own Contribution, loan, subsidy and Funding Gap from the best Scheme (TRD §5.9).

    Adds own_contribution, funding_gap, loan and subsidy figures to `reg`.
    V2 must add at least one assert check.
    """
    assert isinstance(input, IntakeInput)
    assert isinstance(cost, CostBreakdown)
    assert isinstance(reg, FigureRegistry)

    project_cost = int(cost.project_cost.value)
    own_contrib = int(input.own_contribution)
    gap = max(0, project_cost - own_contrib)

    fig_own = reg.add(
        Figure(
            id="own_contribution",
            label="Own Contribution",
            value=float(own_contrib),
            unit="INR",
            source="user",
        )
    )

    fig_gap = reg.add(
        Figure(
            id="funding_gap",
            label="Funding Gap",
            value=float(gap),
            unit="INR",
            source="computed",
            formula="project_cost - own_contribution",
            inputs={
                "project_cost": float(project_cost),
                "own_contribution": float(own_contrib),
            },
        )
    )

    if best is not None:
        loan_val = int(best.terms.principal)
        subsidy_val = int(getattr(best, "subsidy_amount", 0) or 0)
        subsidy_backended = bool(getattr(best, "subsidy_backended", False))
        formula_loan = f"funding_gap (within {best.name} maximum)"
        subsidy_note = None if subsidy_val > 0 else f"{best.name} has no capital subsidy"
    else:
        loan_val = gap
        subsidy_val = 0
        subsidy_backended = False
        formula_loan = "funding_gap"
        subsidy_note = "No eligible scheme"

    fig_loan = reg.add(
        Figure(
            id="loan",
            label="Loan",
            value=float(loan_val),
            unit="INR",
            source="computed",
            formula=formula_loan,
            inputs={"funding_gap": float(gap)},
        )
    )

    fig_sub = reg.add(
        Figure(
            id="subsidy",
            label="Subsidy",
            value=float(subsidy_val),
            unit="INR",
            source="scheme",
            note=subsidy_note,
        )
    )

    return MeansOfFinance(
        own_contribution=fig_own,
        loan=fig_loan,
        subsidy=fig_sub,
        subsidy_backended=subsidy_backended,
        funding_gap=fig_gap,
    )



def break_even_month(
    ops: list[tuple[int, int]],
    schedule: list[RepaymentRow],
    reg: FigureRegistry,
) -> Figure:
    """First month where revenue − opex − payment ≥ 0 (TRD §5.6).

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.finance.break_even_month")


def payback_months(
    ops: list[tuple[int, int]],
    project_cost: int,
    reg: FigureRegistry,
) -> Figure:
    """First month where cumulative (revenue − opex) ≥ project_cost, else NOT_PAID_BACK (TRD §5.6).

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.finance.payback_months")


def min_dscr(projections: list[YearProjection], reg: FigureRegistry) -> Figure:
    """Minimum DSCR over years with debt service (TRD §5.6). Value when there is no debt service is open.

    V2 must add at least one assert check.
    """
    raise NotImplementedError("engine.finance.min_dscr")
