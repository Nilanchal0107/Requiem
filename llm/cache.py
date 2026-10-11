"""Recorded LLM responses: live | record | replay (TRD §6.2). Cache files are committed under data/llm_cache/."""
from enum import StrEnum
from typing import Any


class CacheMode(StrEnum):
    """Closed set. `live` ignores the cache, `record` writes it, `replay` reads only and raises on a miss."""

    LIVE = "live"
    RECORD = "record"
    REPLAY = "replay"


import hashlib
import json


def cache_key(model: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None) -> str:
    """sha256 of model + json(messages) + json(tools) (TRD §6.2). Names the file data/llm_cache/<key>.json.

    V2 must add at least one assert check.
    """
    assert isinstance(model, str), "model must be a string"
    assert isinstance(messages, list), "messages must be a list"

    blob = {
        "model": model,
        "messages": messages,
        "tools": tools or [],
    }
    encoded = json.dumps(blob, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

