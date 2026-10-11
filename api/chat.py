from fastapi import APIRouter, HTTPException

from api.contracts import ChatRequest, ChatResponse, Change, Citation
from api.settings import fixture

router = APIRouter(prefix="/api", tags=["chat"])


# shortcut: one canned answer for the fixture report only, any other report id is 404; V2 runs the LLM tool loop
@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    report = fixture("report.json")
    if body.report_id != report["id"]:
        raise HTTPException(404, "report not found")
    scheme = fixture("schemes.json")[0]
    return ChatResponse(
        reply="Your funding gap is {{funding_gap}}. Borrowing less lowers your EMI.",
        citations=[Citation(scheme_id=scheme["id"], source_url=scheme["source_url"], snippet=scheme["covers"])],
        suggested_changes=[
            Change(field="own_contribution", from_value=report["input"]["own_contribution"], to_value=140000, resulting_verdict="feasible")
        ],
        tools_used=["get_dpr", "search_schemes"],
    )
