"""Scheme matching, eligibility, unlock hints and ranking (TRD §5.4). Pure: no I/O, no LLM, no DB."""
from typing import Any

from api.contracts import IntakeInput, SchemeMatch


def _eval_condition(cond: dict[str, Any], context: dict[str, Any]) -> bool:
    field = cond["field"]
    op = cond["op"]
    target = cond["value"]

    # Resolve field from context (e.g. eligibility.age, project_cost, sector, special_category, is_rural)
    parts = field.split(".")
    val = context
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        else:
            val = getattr(val, p, None)

    if op == "eq":
        return val == target
    elif op == "gte":
        return val is not None and val >= target
    elif op == "lte":
        return val is not None and val <= target
    elif op == "gt":
        return val is not None and val > target
    elif op == "lt":
        return val is not None and val < target
    elif op == "in":
        return val in target if isinstance(target, (list, tuple, set)) else False
    return False


def _eval_when(when_list: list[dict[str, Any]], context: dict[str, Any]) -> bool:
    if not when_list:
        return True
    return all(_eval_condition(c, context) for c in when_list)


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
    assert isinstance(input, IntakeInput)
    assert isinstance(archetype, dict)
    assert isinstance(schemes, list)
    assert project_cost >= 0

    from api.contracts import IneligibleScheme, SchemeOption
    from engine.finance import build_loan_terms

    # Prepare context
    special_category = (
        input.eligibility.gender in ("female", "other")
        or input.eligibility.social_category in ("sc", "st", "obc")
    )
    is_rural = True  # In Niphad villages / demo

    ctx: dict[str, Any] = {
        "eligibility": input.eligibility,
        "input": input,
        "archetype": archetype,
        "archetype_id": archetype.get("id", input.archetype_id),
        "sector": archetype.get("sector"),
        "project_cost": project_cost,
        "special_category": special_category,
        "is_rural": is_rural,
    }

    funding_gap = max(0, project_cost - input.own_contribution)

    eligible_options: list[SchemeOption] = []
    ineligible_options: list[IneligibleScheme] = []

    for scheme in schemes:
        s_id = scheme["id"]
        s_name = scheme["name"]
        s_sectors = scheme.get("sectors", [])

        # 1. Sector check
        arch_sector = archetype.get("sector")
        if arch_sector and s_sectors and arch_sector not in s_sectors:
            ineligible_options.append(
                IneligibleScheme(
                    scheme_id=s_id,
                    name=s_name,
                    failed_rule=f"Sector '{arch_sector}' is not covered by {s_name}",
                    unlock_hint=None,
                )
            )
            continue

        # 2. Evaluate rules
        failed_rule_msg = None
        for rule in scheme.get("rules", []):
            when_conds = rule.get("when", [])
            if _eval_when(when_conds, ctx):
                if not _eval_condition(rule, ctx):
                    failed_rule_msg = rule.get("message", f"Failed condition on {rule.get('field')}")
                    break

        if failed_rule_msg:
            # Check for unlock hint on project_cost / education
            unlock_hint = None
            if "project_cost" in failed_rule_msg or "₹5 lakh" in failed_rule_msg:
                unlock_hint = "Reduce project scale or choose an eligible trade"
            elif s_id == "standup_india" and project_cost < 1000000:
                needed = 1000000 - project_cost
                unlock_hint = f"Increase project cost to at least ₹10 lakh (need ₹{needed:,})"
            ineligible_options.append(
                IneligibleScheme(
                    scheme_id=s_id,
                    name=s_name,
                    failed_rule=failed_rule_msg,
                    unlock_hint=unlock_hint,
                )
            )
            continue

        # 3. Check Own Contribution
        # Find required own contribution pct
        min_own_pct = 0
        for entry in scheme.get("own_contribution_pct", []):
            if _eval_when(entry.get("when", []), ctx):
                min_own_pct = entry["pct"]
                break

        min_own_amt = round(project_cost * (min_own_pct / 100.0))
        if input.own_contribution < min_own_amt:
            diff = min_own_amt - input.own_contribution
            ineligible_options.append(
                IneligibleScheme(
                    scheme_id=s_id,
                    name=s_name,
                    failed_rule=f"Own contribution is below required {min_own_pct}% of project cost (₹{min_own_amt:,})",
                    unlock_hint=f"₹{diff:,} more Own Contribution",
                )
            )
            continue

        # 4. Subsidy calculation
        sub_cfg = scheme.get("subsidy", {})
        sub_type = sub_cfg.get("type", "none")
        sub_pct = 0
        if sub_type != "none":
            for r_entry in sub_cfg.get("rates", []):
                if _eval_when(r_entry.get("when", []), ctx):
                    sub_pct = r_entry["pct"]
                    break

        # Max subsidy or subsidy amount
        subsidy_amt = round(project_cost * (sub_pct / 100.0))

        # Loan principal
        if sub_type == "capital_upfront":
            principal = max(0, funding_gap - subsidy_amt)
        else:
            principal = funding_gap

        # Check maximum loan and tiers
        loan_cfg = scheme.get("loan", {})
        scheme_max_loan = loan_cfg.get("max", float("inf"))
        tiers = scheme.get("tiers", [])

        matched_tier_id = None
        if tiers:
            # e.g. MUDRA tiers: find tier where principal <= max_loan and when conditions match
            # Tiers sorted ascending by max_loan: shishu (50k), kishore (5L), tarun (10L), tarun_plus (20L)
            for tier in tiers:
                if _eval_when(tier.get("when", []), ctx):
                    if principal <= tier["max_loan"]:
                        matched_tier_id = tier["id"]
                        break
            if not matched_tier_id:
                # Principal exceeds all available tiers
                ineligible_options.append(
                    IneligibleScheme(
                        scheme_id=s_id,
                        name=s_name,
                        failed_rule=f"Funding Gap ₹{principal:,} exceeds maximum loan limit for {s_name}",
                        unlock_hint=f"Increase Own Contribution or reduce project cost to fit within tier limits",
                    )
                )
                continue
        else:
            if principal > scheme_max_loan:
                diff = principal - scheme_max_loan
                ineligible_options.append(
                    IneligibleScheme(
                        scheme_id=s_id,
                        name=s_name,
                        failed_rule=f"Funding Gap ₹{principal:,} exceeds maximum loan of ₹{scheme_max_loan:,}",
                        unlock_hint=f"₹{diff:,} more Own Contribution",
                    )
                )
                continue

        # Build loan terms
        terms = build_loan_terms(principal, scheme, input.tenure_months)

        # Calculate effective rate for ranking
        # TRD: "rate minus interest subvention, minus the annualised value of a capital subsidy over the tenure"
        tenure_years = terms.tenure_months / 12.0
        annualised_sub_pct = (sub_pct / tenure_years) if (tenure_years > 0 and sub_pct > 0) else 0.0
        eff_rate = terms.interest_rate - annualised_sub_pct

        reasons = [
            f"{archetype.get('name', 'Business')} in {arch_sector or 'allied'} sector is covered",
        ]
        if matched_tier_id:
            reasons.append(f"Funding Gap fits the {matched_tier_id.capitalize()} tier")
        if sub_pct > 0:
            reasons.append(f"{sub_pct}% capital subsidy under {s_name}")

        opt = SchemeOption(
            scheme_id=s_id,
            name=s_name,
            tier=matched_tier_id,
            terms=terms,
            effective_rate=round(eff_rate, 2),
            reasons=reasons,
            source_url=scheme.get("source_url", ""),
        )
        eligible_options.append(opt)


    # Rank eligible options by effective_rate ascending
    eligible_options.sort(key=lambda o: o.effective_rate)

    best = eligible_options[0] if eligible_options else None
    alternatives = eligible_options[1:] if len(eligible_options) > 1 else []

    return SchemeMatch(
        best=best,
        alternatives=alternatives,
        ineligible=ineligible_options,
    )

