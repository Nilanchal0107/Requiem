from fastapi import APIRouter, HTTPException

from api.contracts import ArchetypeSummary, Block, District, SchemeSummary, Village

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/localities", response_model=list[District] | list[Block] | list[Village])
def localities(district: str | None = None, block: str | None = None):
    """No params: districts. `district`: blocks. `district` + `block`: villages."""
    raise HTTPException(501)


@router.get("/archetypes", response_model=list[ArchetypeSummary])
def archetypes():
    raise HTTPException(501)


@router.get("/schemes", response_model=list[SchemeSummary])
def schemes():
    raise HTTPException(501)
