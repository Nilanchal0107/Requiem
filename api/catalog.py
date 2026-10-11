from fastapi import APIRouter, HTTPException

from api.contracts import ArchetypeSummary, Block, District, SchemeSummary, Village
from api.settings import fixture

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/localities", response_model=list[District] | list[Block] | list[Village])
def localities(district: str | None = None, block: str | None = None):
    """No params: districts. `district`: blocks. `district` + `block`: villages."""
    data = fixture("localities.json")
    # Model instances, not dicts: a union response model would otherwise match a Block dict as a District and drop its fields.
    if block is not None:
        if not any(b["code"] == block and b["district_code"] == district for b in data["blocks"]):
            raise HTTPException(404, "block not found")
        return [Village(**v) for v in data["villages"] if v["block_code"] == block]
    if district is not None:
        return [Block(**b) for b in data["blocks"] if b["district_code"] == district]
    return [District(**d) for d in data["districts"]]


@router.get("/archetypes", response_model=list[ArchetypeSummary])
def archetypes():
    return fixture("archetypes.json")


@router.get("/schemes", response_model=list[SchemeSummary])
def schemes():
    return fixture("schemes.json")
