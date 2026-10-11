"""Entrepreneur View and Comparison paragraph (TRD §6.3, §4.3). Prompts in llm/prompts/."""
from api.contracts import EngineResult, Explanation, Language


def explain_report(result: EngineResult, language: Language) -> Explanation:
    """Entrepreneur View: prompt gets EngineResult without repayment rows, a figure table and the language.

    Returns sections and SWOT with `verified`, `total`, `regenerated`. If both providers fail, returns
    `available=False` with empty sections (TRD §6). Verifier runs on each section and SWOT line.
    V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.explain.explain_report")


def explain_comparison(results: list[EngineResult], language: Language) -> str:
    """Comparison summary paragraph. Placeholders are `<archetype_id>.<figure_id>`; same verifier as the report.

    `results` is in the request's archetype order. V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.explain.explain_comparison")
