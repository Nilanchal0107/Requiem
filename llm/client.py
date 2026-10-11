"""LLM client: OpenAI SDK, provider switch and one fallback (TRD §6.1). The only module that talks to providers."""
from typing import Any, TypeVar

from openai.types.chat import ChatCompletion
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def complete(
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    json: bool = False,
    temperature: float = 0.3,
) -> ChatCompletion:
    """Call LLM_PRIMARY; on error or after LLM_TIMEOUT_S retry once on the other provider (TRD §6.1).

    `json=True` sets response_format to json_object. Temperature is 0.3 for explanations, 0 for intake.
    Cache mode (TRD §6.2) is applied here. V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.client.complete")


def complete_json(messages: list[dict[str, Any]], schema: type[T], *, temperature: float = 0.0) -> T:
    """Call `complete(json=True)`, validate the JSON against `schema`, retry once with the error sent back (TRD §6.1).

    Returns the validated model. V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.client.complete_json")
