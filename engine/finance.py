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
    raise NotImplementedError("engine.finance.build_means_of_finance")


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
