"""Free text to a partial IntakeInput (TRD §6.4). The Entrepreneur confirms the result in the form."""
import logging
from typing import Annotated, Any

from pydantic import TypeAdapter, ValidationError

from api.contracts import Eligibility, IntakeInput, IntakeParseRequest, IntakeParseResponse
from llm.client import complete

log = logging.getLogger(__name__)

_PROMPT = "intake_parse.md"
_ELIGIBILITY_KEYS = list(Eligibility.model_fields)
# The form always has to collect these; the other IntakeInput fields have defaults.
_REQUIRED = [
    "village_code",
    "archetype_id",
    "unit_scale",
    "own_contribution",
    "eligibility.age",
    "eligibility.gender",
    "eligibility.social_category",
    "eligibility.education",
]


def _field_validator(model: Any, key: str) -> TypeAdapter:
    f = model.model_fields[key]
    return TypeAdapter(Annotated[(f.annotation, *f.metadata)] if f.metadata else f.annotation)


def parse_intake(request: IntakeParseRequest, archetype_ids: list[str]) -> IntakeParseResponse:
    """LLM (TRD §6.4; temperature 0, json) extracts fields from free text. Unknown archetypes are dropped.

    `missing` is filled by `missing_fields`, never by the model.
    """
    from pathlib import Path
    import json

    assert request.text.strip(), "text must not be empty"
    system = (Path(__file__).parent / "prompts" / _PROMPT).read_text(encoding="utf-8").replace(
        "{archetype_ids}", ", ".join(archetype_ids)
    )
    raw: dict[str, Any] = {}
    try:
        resp = complete(
            [{"role": "system", "content": system}, {"role": "user", "content": request.text}],
            json=True,
            temperature=0,
        )
        parsed = json.loads(resp.choices[0].message.content or "{}")
        raw = parsed if isinstance(parsed, dict) else {}
    except Exception as exc:  # noqa: BLE001 - the form still works with nothing prefilled
        log.warning("parse_intake: LLM call failed: %s", exc)

    fields: dict[str, Any] = {}
    if raw.get("archetype_id") in archetype_ids:
        fields["archetype_id"] = raw["archetype_id"]
    for key in ("unit_scale", "own_contribution"):
        try:
            fields[key] = _field_validator(IntakeInput, key).validate_python(raw.get(key))
        except ValidationError:
            pass
    if "unit_scale" in fields and fields["unit_scale"] <= 0:
        del fields["unit_scale"]
    elig: dict[str, Any] = {}
    for key in _ELIGIBILITY_KEYS:
        if key in raw:
            try:
                elig[key] = _field_validator(Eligibility, key).validate_python(raw[key])
            except ValidationError:
                pass  # out of range or not in the enum: leave it for the form
    if elig:
        fields["eligibility"] = elig
    return IntakeParseResponse(fields=fields, missing=missing_fields(fields))


def missing_fields(fields: dict[str, Any]) -> list[str]:
    """Dot paths of IntakeInput fields the form still has to collect. Pure, computed in code (TRD §6.4)."""
    assert isinstance(fields, dict), "fields must be a dict"
    out = []
    for path in _REQUIRED:
        node: Any = fields
        for part in path.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if node is None:
            out.append(path)
    return out
