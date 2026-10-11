"""LLM client: OpenAI SDK, provider switch and one fallback (TRD §6.1). The only module that talks to providers."""
from typing import Any, TypeVar

from openai.types.chat import ChatCompletion
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


import json as json_lib
import os
from pathlib import Path

from openai import OpenAI
from openai.types.chat import ChatCompletion

from llm.cache import CacheMode, cache_key

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "llm_cache"


def _get_provider_config(provider: str) -> tuple[str, str, str]:
    if provider == "groq":
        base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        api_key = os.getenv("GROQ_API_KEY", "")
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    else:  # gemini
        base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
        api_key = os.getenv("GEMINI_API_KEY", "")
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    return base_url, api_key, model


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
    assert isinstance(messages, list), "messages must be a list"
    assert len(messages) > 0, "messages must not be empty"

    mode_str = os.getenv("LLM_MODE", CacheMode.REPLAY.value).lower()
    mode = CacheMode(mode_str) if mode_str in [m.value for m in CacheMode] else CacheMode.REPLAY
    primary = os.getenv("LLM_PRIMARY", "gemini").lower()
    fallback = "groq" if primary == "gemini" else "gemini"

    _, _, primary_model = _get_provider_config(primary)
    key = cache_key(primary_model, messages, tools)
    cache_path = _DATA_DIR / f"{key}.json"

    # 1. Replay mode: must read from cache; raise on miss
    if mode == CacheMode.REPLAY:
        if not cache_path.is_file():
            raise FileNotFoundError(f"Cache miss in replay mode for key {key} (file {cache_path})")
        data = json_lib.loads(cache_path.read_text(encoding="utf-8"))
        return ChatCompletion.model_validate(data)

    # 2. Live or Record mode: call provider with fallback
    response_format = {"type": "json_object"} if json else None
    timeout = float(os.getenv("LLM_TIMEOUT_S", "15"))

    def _call(prov: str, model: str | None = None) -> ChatCompletion:
        b_url, a_key, mod = _get_provider_config(prov)
        mod = model or mod
        # max_retries=0: the SDK otherwise sleeps through 429s (up to ~40 s); falling over to the other provider is faster
        client = OpenAI(base_url=b_url, api_key=a_key, timeout=timeout, max_retries=0)
        kwargs: dict[str, Any] = {
            "model": mod,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        if response_format:
            kwargs["response_format"] = response_format
        return client.chat.completions.create(**kwargs)

    # Groq rate limits are per model, so more Groq models are cheap extra tries before the other provider.
    backups = [m.strip() for m in os.getenv("GROQ_BACKUP_MODELS", "qwen/qwen3.8-27b,openai/gpt-oss-20b").split(",") if m.strip()]
    attempts = [(primary, None), *(("groq", m) for m in backups), (fallback, None)]
    res: ChatCompletion | None = None
    for i, (prov, model) in enumerate(attempts):
        try:
            res = _call(prov, model)
            break
        except Exception:
            if i == len(attempts) - 1:
                raise
    assert res is not None

    if mode == CacheMode.RECORD:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(res.model_dump_json(), encoding="utf-8")

    return res


def complete_json(messages: list[dict[str, Any]], schema: type[T], *, temperature: float = 0.0) -> T:
    """Call `complete(json=True)`, validate the JSON against `schema`, retry once with the error sent back (TRD §6.1).

    Returns the validated model. V2 must add at least one assert check.
    """
    assert isinstance(messages, list), "messages must be a list"
    assert issubclass(schema, BaseModel), "schema must be a Pydantic model"

    resp = complete(messages, json=True, temperature=temperature)
    content = resp.choices[0].message.content or "{}"

    try:
        parsed = json_lib.loads(content)
        return schema.model_validate(parsed)
    except Exception as err:
        # Retry once with the error sent back
        retry_messages = list(messages) + [
            {"role": "assistant", "content": content},
            {
                "role": "user",
                "content": f"The response was invalid JSON or did not match the expected schema: {err}. Please return strictly valid JSON matching the schema.",
            },
        ]
        resp2 = complete(retry_messages, json=True, temperature=temperature)
        content2 = resp2.choices[0].message.content or "{}"
        parsed2 = json_lib.loads(content2)
        return schema.model_validate(parsed2)

