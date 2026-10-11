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


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, supporting Hindi/Marathi danda (।), ., ?, !, newlines.
    Masks placeholders first so dots within placeholder ids do not split sentences.
    """
    placeholder_map: dict[str, str] = {}

    def mask(m: re.Match) -> str:
        k = f"__PH_{len(placeholder_map)}__"
        placeholder_map[k] = m.group(0)
        return k

    masked = PLACEHOLDER_RE.sub(mask, text)
    raw_parts = re.split(r"(?<=[.!?।\n])\s*", masked)
    sentences: list[str] = []
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        for k, v in placeholder_map.items():
            part = part.replace(k, v)
        sentences.append(part)
    return sentences



def verify(text: str, figures: dict[str, Figure]) -> VerifyResult:
    """Check every `{{id}}` against `figures` (TRD §6.3, steps 1–2) (keys may be namespaced, e.g. `dairy.min_dscr`), then scan the
    text with placeholders removed for raw digits (TRD §6.3 steps 1–2). Splits into sentences for `offending`.
    V2 must add at least one assert check.
    """
    assert isinstance(text, str), "text must be a string"
    assert isinstance(figures, dict), "figures must be a dict"

    sentences = _split_sentences(text)
    if not sentences and text.strip():
        sentences = [text.strip()]

    verified = 0
    offending: list[str] = []

    for sentence in sentences:
        placeholders = PLACEHOLDER_RE.findall(sentence)
        has_unknown = False
        sentence_verified = 0

        for pid in placeholders:
            if pid in figures:
                sentence_verified += 1
            else:
                has_unknown = True

        # Remove placeholders before checking for raw digits
        without_placeholders = PLACEHOLDER_RE.sub("", sentence)
        has_raw_digits = bool(DIGIT_RE.search(without_placeholders))

        if has_unknown or has_raw_digits:
            offending.append(sentence)
        else:
            verified += sentence_verified

    return VerifyResult(verified=verified, offending=offending)

