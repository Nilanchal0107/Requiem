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
    assert principal >= 0, "principal must be non-negative"
    assert isinstance(scheme, dict), "scheme must be a dict"

    loan_cfg = scheme.get("loan", {})
    annual_rate = float(loan_cfg.get("interest_rate", 10.0))
    tenure = int(tenure_months if tenure_months is not None else loan_cfg.get("max_tenure_months", 60))
    moratorium = int(loan_cfg.get("moratorium_months", 0))
    moratorium_mode = loan_cfg.get("moratorium_mode", "serviced")
    assert moratorium_mode in ("capitalised", "serviced")

    r = annual_rate / 12.0 / 100.0
    n = tenure - moratorium

    if principal == 0 or n <= 0:
        return LoanTerms(
            principal=principal,
            interest_rate=annual_rate,
            tenure_months=tenure,
            moratorium_months=moratorium,
            moratorium_mode=moratorium_mode,
            emi=0,
            total_interest=0,
        )

    if moratorium_mode == "capitalised":
        p_prime = principal * ((1.0 + r) ** moratorium)
    else:
        p_prime = float(principal)

    if r == 0:
        emi = round(p_prime / n)
    else:
        emi = round(p_prime * r * ((1.0 + r) ** n) / (((1.0 + r) ** n) - 1.0))

    # Calculate total interest by running simulation
    opening = float(principal)
    total_interest = 0
    for m in range(1, tenure + 1):
        interest = round(opening * r)
        total_interest += interest
        if m <= moratorium:
            if moratorium_mode == "capitalised":
                opening += interest
            # if serviced, interest is paid so opening remains constant
        else:
            if m == tenure:
                opening = 0
            else:
                principal_paid = emi - interest
                opening = max(0.0, opening - principal_paid)

    return LoanTerms(
        principal=principal,
        interest_rate=annual_rate,
        tenure_months=tenure,
        moratorium_months=moratorium,
        moratorium_mode=moratorium_mode,
        emi=emi,
        total_interest=total_interest,
    )


def repayment_schedule(terms: LoanTerms, scheme: dict[str, Any], subsidy: int) -> list[RepaymentRow]:
    """Month-by-month schedule closing at exactly 0, with PMEGP back-ended subsidy applied at lock-in (TRD §5.5).

    V2 must add at least one assert check.
    """
    assert isinstance(terms, LoanTerms)
    assert isinstance(scheme, dict)
    assert subsidy >= 0, "subsidy must be non-negative"

    if terms.principal == 0 or terms.tenure_months == 0:
        return []

    r = terms.interest_rate / 12.0 / 100.0
    tenure = terms.tenure_months
    moratorium = terms.moratorium_months
    moratorium_mode = terms.moratorium_mode
    emi = terms.emi

    sub_cfg = scheme.get("subsidy", {})
    is_backended = sub_cfg.get("type") == "capital_backended" and subsidy > 0
    lock_in = int(sub_cfg.get("lock_in_months", 0))

    opening = terms.principal
    rows: list[RepaymentRow] = []

    for m in range(1, tenure + 1):
        # Check backended subsidy at end of lock-in month
        interest = round(opening * r)

        if m <= moratorium:
            if moratorium_mode == "capitalised":
                principal_paid = 0
                payment = 0
                closing = opening + interest
            else:  # serviced
                principal_paid = 0
                payment = interest
                closing = opening
        else:
            if m == tenure:
                principal_paid = opening
                payment = principal_paid + interest
                closing = 0
            else:
                principal_paid = emi - interest
                payment = emi
                closing = opening - principal_paid

        # PMEGP subsidy applied at month lock_in_months: reduces outstanding principal, recomputing EMI
        if is_backended and m == lock_in:
            closing = max(0, closing - subsidy)
            rem_n = tenure - m
            if rem_n > 0 and closing > 0:
                if r == 0:
                    emi = round(closing / rem_n)
                else:
                    emi = round(closing * r * ((1.0 + r) ** rem_n) / (((1.0 + r) ** rem_n) - 1.0))

        rows.append(
            RepaymentRow(
                month=m,
                opening=opening,
                interest=interest,
                principal=principal_paid,
                payment=payment,
                closing=closing,
            )
        )
        opening = closing

    return rows


def monthly_operating(
    input: IntakeInput,
    archetype: dict[str, Any],
    market: MarketAnalysis,
) -> list[tuple[int, int]]:
    """(revenue, operating_cost) for each of the 60 months (TRD §5.3).

    V2 must add at least one assert check.
    """
    assert isinstance(input, IntakeInput)
    assert isinstance(archetype, dict)
    assert isinstance(market, MarketAnalysis)

    from engine.market import our_capacity, sales_ceiling

    cap = our_capacity(input, archetype)
    ceil = sales_ceiling(input, archetype, market)

    ramp_up = int(archetype.get("ramp_up_months", 1))
    target_util = float(archetype.get("target_utilisation_pct", 100)) / 100.0
    price = float(archetype["revenue"]["price"])
    growth_pct = float(archetype.get("growth_pct_per_year", 0.0) or 0.0) / 100.0

    op_cfg = archetype.get("operating_cost", {})
    var_pct = float(op_cfg.get("variable_pct_of_revenue", 0.0)) / 100.0
    fixed_monthly = int(op_cfg.get("fixed_monthly", 0))

    ops: list[tuple[int, int]] = []
    for m in range(1, HORIZON_MONTHS + 1):
        util = target_util * min(1.0, m / ramp_up)
        # In fixture, when archetype growth_pct_per_year is not set or base is reached:
        year_idx = (m - 1) // 12
        growth_factor = (1.0 + growth_pct) ** year_idx
        units = min(cap * util, ceil) * growth_factor
        rev = round(units * price)
        opex = round(rev * var_pct + fixed_monthly)
        ops.append((rev, opex))

    return ops


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
    assert isinstance(input, IntakeInput)
    assert isinstance(cost, CostBreakdown)
    assert len(schedule) <= HORIZON_MONTHS or True

    ops = monthly_operating(input, archetype, market)

    # Calculate annual straight-line depreciation
    cost_items_raw = archetype.get("cost_items", [])
    depr_annual = 0
    for item in cost_items_raw:
        item_id = item["id"]
        fixed = int(item.get("fixed", 0))
        per_unit = int(item.get("per_unit", 0))
        item_val = round(fixed + per_unit * input.unit_scale)
        depr_pct = float(item.get("depreciation_pct", 0)) / 100.0
        depr_annual += round(item_val * depr_pct)

    projections: list[YearProjection] = []
    sched_by_month = {r.month: r for r in schedule}

    for y in range(1, 6):
        start_m = (y - 1) * 12 + 1
        end_m = y * 12

        rev_y = sum(ops[m - 1][0] for m in range(start_m, end_m + 1))
        opex_y = sum(ops[m - 1][1] for m in range(start_m, end_m + 1))

        interest_y = sum(sched_by_month[m].interest for m in range(start_m, end_m + 1) if m in sched_by_month)
        principal_y = sum(sched_by_month[m].principal for m in range(start_m, end_m + 1) if m in sched_by_month)

        net_profit_y = rev_y - opex_y - depr_annual - interest_y
        cash_flow_y = net_profit_y + depr_annual - principal_y
        debt_service_y = principal_y + interest_y

        dscr_y = (
            round((net_profit_y + depr_annual + interest_y) / debt_service_y, 2)
            if debt_service_y > 0
            else None
        )

        projections.append(
            YearProjection(
                year=y,
                revenue=rev_y,
                operating_cost=opex_y,
                depreciation=depr_annual,
                interest=interest_y,
                net_profit=net_profit_y,
                cash_flow=cash_flow_y,
                debt_service=debt_service_y,
                dscr=dscr_y,
            )
        )

    return projections



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
        formula_loan = f"funding_gap (within {best.name} maximum)"
        # Check subsidy: if MUDRA, type is none. If PMEGP, capital_backended.
        # If principal and cost allow subsidy, e.g. for PMEGP:
        # PMEGP has rates: 35% rural special_category, 25% rural general, 15% urban
        if "pmegp" in best.scheme_id:
            special_category = (
                input.eligibility.gender in ("female", "other")
                or input.eligibility.social_category in ("sc", "st", "obc")
            )
            pct = 35 if special_category else 25
            subsidy_val = round(project_cost * (pct / 100.0))
            subsidy_backended = True
            subsidy_note = f"{pct}% capital subsidy under PMEGP (back-ended, 36-month lock-in)"
        else:
            subsidy_val = 0
            subsidy_backended = False
            subsidy_note = f"{best.name} has no capital subsidy"
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
    assert isinstance(ops, list)
    assert isinstance(reg, FigureRegistry)

    payments = {r.month: r.payment for r in schedule}
    be_m = NOT_PAID_BACK

    for m in range(1, len(ops) + 1):
        rev, opex = ops[m - 1]
        pmt = payments.get(m, 0)
        if rev - opex - pmt >= 0:
            be_m = m
            break

    return reg.add(
        Figure(
            id="break_even_month",
            label="Break-even month",
            value=float(be_m),
            unit="months",
            source="computed",
            formula="first month where revenue - operating cost - payment >= 0",
        )
    )


def payback_months(
    ops: list[tuple[int, int]],
    project_cost: int,
    reg: FigureRegistry,
) -> Figure:
    """First month where cumulative (revenue − opex) ≥ project_cost, else NOT_PAID_BACK (TRD §5.6).

    V2 must add at least one assert check.
    """
    assert isinstance(ops, list)
    assert project_cost >= 0
    assert isinstance(reg, FigureRegistry)

    cum_margin = 0
    pb_m = NOT_PAID_BACK

    for m in range(1, len(ops) + 1):
        rev, opex = ops[m - 1]
        cum_margin += (rev - opex)
        if cum_margin >= project_cost:
            pb_m = m
            break

    return reg.add(
        Figure(
            id="payback_months",
            label="Payback",
            value=float(pb_m),
            unit="months",
            source="computed",
            formula="first month where cumulative (revenue - operating cost) >= project_cost",
        )
    )


def min_dscr(projections: list[YearProjection], reg: FigureRegistry) -> Figure:
    """Minimum DSCR over years with debt service (TRD §5.6). Value when there is no debt service is open.

    V2 must add at least one assert check.
    """
    assert isinstance(projections, list)
    assert isinstance(reg, FigureRegistry)

    valid_dscrs = [p.dscr for p in projections if p.dscr is not None]
    val = min(valid_dscrs) if valid_dscrs else 0.0

    return reg.add(
        Figure(
            id="min_dscr",
            label="Lowest DSCR",
            value=float(val),
            unit="ratio",
            source="computed",
            formula="min over years of (net_profit + depreciation + interest) / debt_service",
        )
    )

