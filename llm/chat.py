"""Chat advisor tool loop (TRD §6.5, §4.4). Never writes to the DB."""
from typing import Any, Callable

from api.contracts import (
    ChatResponse,
    ChatTurn,
    Change,
    EngineResult,
    Language,
    Report,
)
from llm.retrieval import SchemeIndex

# Injected by api/: runs run_engine with the changes applied. Keeps llm off the catalogue and the DB.
WhatIf = Callable[[list[Change]], EngineResult]


def chat(
    report: Report,
    message: str,
    history: list[ChatTurn],
    language: Language,
    *,
    index: SchemeIndex,
    what_if: WhatIf,
) -> ChatResponse:
    """Tool loop of at most 3 rounds over get_dpr, search_schemes and simulate, then the verifier on the reply.

    Simulate figures get the `sim.` prefix in `ChatResponse.figures`. Each simulate result becomes a
    `suggested_changes` entry. V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.chat.chat")


def tool_get_dpr(engine: EngineResult, section: str) -> dict[str, Any]:
    """Return one part of the stored EngineResult (e.g. market, cost, schemes, finance, verdict).

    V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.chat.tool_get_dpr")


def tool_simulate(what_if: WhatIf, changes: list[Change]) -> EngineResult:
    """Run the what-if with `changes` applied. The caller reads `.verdict` for `resulting_verdict`.

    V2 must add at least one assert check.
    """
    raise NotImplementedError("llm.chat.tool_simulate")
