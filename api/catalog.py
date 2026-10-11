from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from api import db, live
from api.contracts import ArchetypeSummary, Block, District, SchemeSummary, Village
from api.deps import get_session

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/localities", response_model=list[District] | list[Block] | list[Village])
def localities(district: str | None = None, block: str | None = None, session: Session = Depends(get_session)):
    """No params: districts. `district`: blocks. `district` + `block`: villages."""
    rows = session.exec(select(db.Village)).all()
    # Model instances, not dicts: a union response model would otherwise match a Block dict as a District and drop its fields.
    if block is not None:
        found = [Village(**r.model_dump()) for r in rows if r.block_code == block and r.district_code == district]
        if not found:
            raise HTTPException(404, "block not found")
        return found
    if district is not None:
        blocks = {r.block_code: r.block_name for r in rows if r.district_code == district}
        return [Block(code=c, name=n, district_code=district) for c, n in blocks.items()]
    return [District(code=c, name=n) for c, n in {r.district_code: r.district_name for r in rows}.items()]


@router.get("/archetypes", response_model=list[ArchetypeSummary])
def archetypes():
    return [
        ArchetypeSummary(
            id=a["id"], name=a["name"], sector={"agri": "agriculture"}.get(a["sector"], a["sector"]), unit_label=a["unit_label"],
            unit_scale_default=a["unit_scale"]["default"], unit_scale_min=a["unit_scale"]["min"],
            unit_scale_max=a["unit_scale"]["max"], unit_scale_step=a["unit_scale"]["step"],
            eligibility_fields=a["eligibility_fields"],
        )
        for a in live.archetypes().values()
    ]


def _subsidy(s: dict) -> str | None:
    pcts = [r["pct"] for r in s["subsidy"]["rates"]]
    if s["subsidy"]["type"] == "none" or not pcts:
        return None
    lo, hi = min(pcts), max(pcts)
    kind = s["subsidy"]["type"].replace("_", " ")
    return f"{lo:g}% of project cost, {kind}" if lo == hi else f"{lo:g}–{hi:g}%, {kind}"


@router.get("/schemes", response_model=list[SchemeSummary])
def schemes():
    return [
        SchemeSummary(
            id=s["id"], name=s["name"], covers=s["covers"],
            max_loan=int(max([s["loan"]["max"], *(t["max_loan"] for t in s["tiers"])])),
            interest_rate_min=s["loan"]["interest_rate"], interest_rate_max=s["loan"]["interest_rate"],
            max_tenure_months=s["loan"]["max_tenure_months"], moratorium_months=s["loan"]["moratorium_months"],
            subsidy=_subsidy(s), source_url=s["source_url"], verified_on=str(s["verified_on"]),
        )
        for s in live.schemes()
    ]
