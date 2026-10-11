"""Placeholder verifier cases (TRD §6.3, seam 3). Skipped until V2 implements llm.verifier.verify."""
import pytest

from api.contracts import Figure
from llm.verifier import verify


def _figure(figure_id: str) -> Figure:
    return Figure(id=figure_id, label=figure_id, value=1.0, unit="INR", source="computed")


FIGURES = {
    "funding_gap": _figure("funding_gap"),
    "dairy.min_dscr": _figure("dairy.min_dscr"),  # Comparison ids are namespaced by archetype
}


def test_accepts_valid_placeholders():
    result = verify("Your funding gap is {{funding_gap}}.", FIGURES)
    assert result.verified == 1
    assert result.offending == []


def test_rejects_ascii_digits():
    result = verify("You need 5 lakh more.", FIGURES)
    assert result.offending == ["You need 5 lakh more."]


def test_rejects_devanagari_digits():
    result = verify("हमें ५ लाख चाहिए।", FIGURES)
    assert len(result.offending) == 1
    assert "५" in result.offending[0]


def test_rejects_unknown_ids():
    result = verify("Your gap is {{made_up_id}}.", FIGURES)
    assert result.verified == 0
    assert len(result.offending) == 1


def test_resolves_namespaced_comparison_ids():
    result = verify("Dairy coverage is {{dairy.min_dscr}}.", FIGURES)
    assert result.verified == 1
    assert result.offending == []


def test_resolves_dotted_group_ids():
    figures = {**FIGURES, "cost.animals": _figure("cost.animals")}
    result = verify("Total animal cost is {{cost.animals}}.", figures)
    assert result.verified == 1
    assert result.offending == []


def test_multiple_sentences_with_mixed_verdict():
    figures = {**FIGURES, "cost.animals": _figure("cost.animals")}
    text = "Animal cost is {{cost.animals}}. You need 5 animals."
    result = verify(text, figures)
    assert result.verified == 1
    assert len(result.offending) == 1
    assert "5" in result.offending[0]


