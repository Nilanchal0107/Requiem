from fastapi import APIRouter, HTTPException

from api.contracts import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    raise HTTPException(501)
