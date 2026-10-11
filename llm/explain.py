"""Entrepreneur View and Comparison paragraph (TRD §6.3, §4.3). Prompts in llm/prompts/."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from api.contracts import (
    EngineResult,
    Explanation,
    ExplanationSection,
    Language,
    Swot,
)
from llm.client import complete
from llm.verifier import verify

log = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

_LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
}

_SECTION_KEYS = ("verdict", "market", "pricing", "risks", "path_to_yes", "next_steps")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _figure_table(result: EngineResult) -> str:
    """Return a human-readable figure table string for use in the prompt."""
    lines: list[str] = []
    for fid, fig in result.figures.items():
        lines.append(f"  {{{{  {fid}  }}}}  →  {fig.label}  [{fig.unit}]")
    return "\n".join(lines) if lines else "(no figures)"


def _abridged_engine(result: EngineResult) -> str:
    """Serialise EngineResult without repayment rows (they are large and not needed by LLM)."""
    d = result.model_dump(mode="json")
    d.pop("repayment", None)
    # Remove the figures dict too — it's already injected as a table
    d.pop("figures", None)
    return json.dumps(d, ensure_ascii=False, indent=2)


def _verdict_signals_text(result: EngineResult) -> str:
    parts = [f"{s.name}={s.level}" for s in result.verdict.signals]
    return ", ".join(parts) if parts else "none"


def _path_to_yes_summary(result: EngineResult) -> str:
    if result.path_to_yes is None or not result.path_to_yes.changes:
        return "none (already feasible)"
    parts = [
        f"{c.field} from {c.from_value} to {c.to_value} → {c.resulting_verdict}"
        for c in result.path_to_yes.changes
    ]
    return "; ".join(parts)


def _best_scheme(result: EngineResult) -> str:
    if result.schemes.best:
        s = result.schemes.best
        return f"{s.name} ({s.scheme_id})"
    return "none eligible"


def _build_system_prompt(result: EngineResult, language: Language) -> str:
    """Render entrepreneur_view.md using simple {key} token replacement.

    We deliberately avoid str.format() because engine_json contains JSON
    curly braces that would confuse the format parser.
    """
    template = (_PROMPTS_DIR / "entrepreneur_view.md").read_text(encoding="utf-8")
    replacements = {
        "{language}": language,
        "{language_name}": _LANGUAGE_NAMES.get(language, language),
        "{figure_table}": _figure_table(result),
        "{archetype_id}": result.archetype_id,
        "{village_code}": result.village_code,
        "{verdict_level}": result.verdict.level,
        "{verdict_signals}": _verdict_signals_text(result),
        "{market_gap_coverage}": result.market.competitor_coverage,
        "{best_scheme}": _best_scheme(result),
        "{path_to_yes_summary}": _path_to_yes_summary(result),
        "{engine_json}": _abridged_engine(result),
    }
    prompt = template
    for token, value in replacements.items():
        prompt = prompt.replace(token, str(value))
    return prompt


def _parse_llm_response(content: str) -> tuple[list[ExplanationSection], Swot] | None:
    """Parse LLM JSON into (sections, swot). Returns None on any parse error."""
    try:
        # Strip markdown code fences if present
        raw = content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
            raw = raw.rsplit("```", 1)[0].strip()
        data = json.loads(raw)

        sections = [
            ExplanationSection(
                key=sec["key"],
                title=sec["title"],
                text=sec["text"],
            )
            for sec in data.get("sections", [])
            if sec.get("key") in _SECTION_KEYS
        ]

        swot_raw = data.get("swot", {})
        swot = Swot(
            strengths=swot_raw.get("strengths", []),
            weaknesses=swot_raw.get("weaknesses", []),
            opportunities=swot_raw.get("opportunities", []),
            threats=swot_raw.get("threats", []),
        )
        return sections, swot
    except Exception as exc:  # noqa: BLE001
        log.warning("Failed to parse LLM response: %s", exc)
        return None


def _verify_explanation(
    sections: list[ExplanationSection],
    swot: Swot,
    figures: dict,
) -> tuple[int, int, list[str]]:
    """Run verifier over all sections and SWOT items.

    Returns (verified_count, offending_sentence_count, offending_sentences).
    """
    all_offending: list[str] = []
    total_verified = 0

    texts: list[str] = [s.text for s in sections]
    for items in (swot.strengths, swot.weaknesses, swot.opportunities, swot.threats):
        texts.extend(items)

    for text in texts:
        res = verify(text, figures)
        total_verified += res.verified
        all_offending.extend(res.offending)

    return total_verified, len(all_offending), all_offending


def _strip_offending_sentences(
    sections: list[ExplanationSection],
    swot: Swot,
    offending_set: set[str],
) -> tuple[list[ExplanationSection], Swot]:
    """Remove sentences that are in offending_set from every section and SWOT item."""

    def _clean(text: str) -> str:
        kept = [s for s in text.split(". ") if s not in offending_set and s + "." not in offending_set]
        return ". ".join(kept)

    def _clean_list(items: list[str]) -> list[str]:
        return [it for it in items if it not in offending_set]

    cleaned_sections = [
        ExplanationSection(key=s.key, title=s.title, text=_clean(s.text))
        for s in sections
    ]
    cleaned_swot = Swot(
        strengths=_clean_list(swot.strengths),
        weaknesses=_clean_list(swot.weaknesses),
        opportunities=_clean_list(swot.opportunities),
        threats=_clean_list(swot.threats),
    )
    return cleaned_sections, cleaned_swot


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def explain_report(result: EngineResult, language: Language) -> Explanation:
    """Entrepreneur View (TRD §6.3): prompt gets EngineResult without repayment rows, a figure table and the language.

    Returns sections and SWOT with `verified`, `total`, `regenerated`. If both providers fail, returns
    `available=False` with empty sections (TRD §6). Verifier runs on each section and SWOT line.
    V2 must add at least one assert check.
    """
    assert isinstance(result, EngineResult), "result must be an EngineResult"
    assert language in _LANGUAGE_NAMES, f"language must be one of {list(_LANGUAGE_NAMES)}"

    system_prompt = _build_system_prompt(result, language)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please generate the Entrepreneur View now."},
    ]

    # --- First attempt ---
    regenerated = False
    sections: list[ExplanationSection] | None = None
    swot: Swot | None = None

    try:
        resp = complete(messages, json=True, temperature=0.3)
        content = resp.choices[0].message.content or "{}"
        parsed = _parse_llm_response(content)
        if parsed:
            sections, swot = parsed
    except Exception as exc:  # noqa: BLE001
        log.warning("explain_report: first LLM call failed: %s", exc)

    # If parse failed, return unavailable
    if sections is None or swot is None:
        return Explanation(
            language=language,
            sections=[],
            swot=Swot(strengths=[], weaknesses=[], opportunities=[], threats=[]),
            verified=0,
            total=0,
            regenerated=False,
            available=False,
        )

    # --- First verification pass ---
    verified, offending_count, offending_sentences = _verify_explanation(sections, swot, result.figures)

    if offending_count > 0:
        # Regenerate once (TRD §6.3 step 4)
        log.info("explain_report: verifier found %d offending sentences, regenerating", offending_count)
        regen_messages = list(messages) + [
            {"role": "assistant", "content": content},
            {
                "role": "user",
                "content": (
                    "Your response contained raw numbers or unknown placeholder ids. "
                    "Offending sentences:\n"
                    + "\n".join(f"  - {s}" for s in offending_sentences)
                    + "\n\nPlease regenerate the full Entrepreneur View, replacing every digit "
                    "with a {{figure_id}} from the Figure Table. Do not invent new ids."
                ),
            },
        ]
        try:
            resp2 = complete(regen_messages, json=True, temperature=0.3)
            content2 = resp2.choices[0].message.content or "{}"
            parsed2 = _parse_llm_response(content2)
            if parsed2:
                sections, swot = parsed2
                regenerated = True
                # Re-verify after regeneration
                verified, offending_count, offending_sentences = _verify_explanation(
                    sections, swot, result.figures
                )
        except Exception as exc:  # noqa: BLE001
            log.warning("explain_report: regeneration call failed: %s", exc)

    # --- Strip remaining offending sentences (TRD §6.3 step 5) ---
    total = verified + offending_count
    if offending_count > 0:
        offending_set = set(offending_sentences)
        sections, swot = _strip_offending_sentences(sections, swot, offending_set)
        # Re-count verified after stripping (stripped sentences don't add to verified)
        verified, _, _ = _verify_explanation(sections, swot, result.figures)

    return Explanation(
        language=language,
        sections=sections,
        swot=swot,
        verified=verified,
        total=total,
        regenerated=regenerated,
        available=True,
    )


def explain_comparison(results: list[EngineResult], language: Language) -> str:
    """Comparison summary paragraph (TRD §4.3, §6.3). Placeholders are `<archetype_id>.<figure_id>`; same verifier as the report.

    `results` is in the request's archetype order. V2 must add at least one assert check.
    """
    assert isinstance(results, list) and len(results) >= 2, "results must be a list of at least 2 EngineResults"
    assert language in _LANGUAGE_NAMES, f"language must be one of {list(_LANGUAGE_NAMES)}"

    # Build namespaced figure registry for verification
    namespaced_figures: dict = {}
    figure_tables_lines: list[str] = []
    results_summary_lines: list[str] = []

    for r in results:
        aid = r.archetype_id
        for fid, fig in r.figures.items():
            namespaced_figures[f"{aid}.{fid}"] = fig
        table_lines = [f"  {{{{{aid}.{fid}}}}}  →  {fig.label}  [{fig.unit}]" for fid, fig in r.figures.items()]
        figure_tables_lines.append(f"### {aid}\n" + "\n".join(table_lines))
        results_summary_lines.append(
            f"- {aid}: verdict={r.verdict.level}, best_scheme={_best_scheme(r)}, "
            f"market_gap_coverage={r.market.competitor_coverage}"
        )

    template = (_PROMPTS_DIR / "comparison.md").read_text(encoding="utf-8")
    cmp_replacements = {
        "{language_name}": _LANGUAGE_NAMES.get(language, language),
        "{figure_tables}": "\n\n".join(figure_tables_lines),
        "{results_summary}": "\n".join(results_summary_lines),
    }
    system_prompt = template
    for token, value in cmp_replacements.items():
        system_prompt = system_prompt.replace(token, str(value))

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please write the comparison paragraph now."},
    ]

    try:
        resp = complete(messages, temperature=0.3)
        paragraph = (resp.choices[0].message.content or "").strip()
    except Exception as exc:  # noqa: BLE001
        log.warning("explain_comparison: LLM call failed: %s", exc)
        return ""

    # Verify and strip offending sentences
    vresult = verify(paragraph, namespaced_figures)
    if vresult.offending:
        # Attempt to strip offending sentences (no regeneration for comparison — single call)
        offending_set = set(vresult.offending)
        cleaned = " ".join(s for s in paragraph.split(". ") if s not in offending_set and s + "." not in offending_set)
        paragraph = cleaned.strip()

    return paragraph
