"""Free text to a partial IntakeInput (TRD §6.4). The Entrepreneur confirms the result in the form."""
from typing import Any

from api.contracts import IntakeParseRequest, IntakeParseResponse


def parse_intake(request: IntakeParseRequest, archetype_ids: list[str]) -> IntakeParseResponse:
    """LLM (temperature 0, json) extracts fields from free text. Unknown archetypes are dropped.

    `missing` is filled by `missing_fields`, never by the model. V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.intake.parse_intake")


def missing_fields(fields: dict[str, Any]) -> list[str]:
    """Dot paths of IntakeInput fields the form still has to collect. Pure, computed in code (TRD §6.4).

    V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.intake.missing_fields")
