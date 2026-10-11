from fastapi import APIRouter, HTTPException

from api.contracts import CompareRequest, Comparison

router = APIRouter(prefix="/api", tags=["compare"])


@router.post("/compare", response_model=Comparison)
def compare(body: CompareRequest):
    raise HTTPException(501)
