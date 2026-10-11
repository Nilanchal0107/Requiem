"""Placeholder verifier (TRD §6.3). Pure: text and figures in, a verdict on the text out."""
import re
from dataclasses import dataclass

from api.contracts import Figure

PLACEHOLDER_RE = re.compile(r"\{\{([a-z0-9_.]+)\}\}")
DIGIT_RE = re.compile(r"[0-9०-९]")  # ASCII and Devanagari


@dataclass(frozen=True)
class VerifyResult:
    """verified: placeholders that resolve to a known figure id.
    offending: sentences holding an unknown id or a raw digit (caller regenerates once, then strips them).
    The caller derives `total` as verified + stripped sentences (TRD §6.3 step 5).
    """

    verified: int
    offending: list[str]


def verify(text: str, figures: dict[str, Figure]) -> VerifyResult:
    """Check every `{{id}}` against `figures` (TRD §6.3, steps 1–2) (keys may be namespaced, e.g. `dairy.min_dscr`), then scan the
    text with placeholders removed for raw digits (TRD §6.3 steps 1–2). Splits into sentences for `offending`.
    V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.verifier.verify")
