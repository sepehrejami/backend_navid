from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..persistence.db import get_session
from ..robot_api.router import get_robot_api_service
from ..robot_api.service import RobotAPIService
from ..realtime_bus.bus import publish_event_nowait

from .schemas import PoiMappingUpsertRequest, PoiMappingRead, AutoMapRequest
from .service import PoiMappingService

router = APIRouter(prefix="/poi-mapping", tags=["poi-mapping"])


@router.get("/mappings", response_model=list[PoiMappingRead])
def list_mappings(session: Session = Depends(get_session)):
    svc = PoiMappingService(session)
    rows = svc.list_all()
    return [PoiMappingRead(kind=r.kind, ref=r.ref, poi_id=r.poi_id, area_id=r.area_id, label=r.label) for r in rows]


@router.get("/mappings/{kind}/{ref}", response_model=PoiMappingRead)
def get_mapping(kind: str, ref: str, session: Session = Depends(get_session)):
    svc = PoiMappingService(session)
    row = svc.get(kind, ref)
    if not row:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return PoiMappingRead(kind=row.kind, ref=row.ref, poi_id=row.poi_id, area_id=row.area_id, label=row.label)


@router.post("/mappings", response_model=PoiMappingRead)
def upsert_mapping(payload: PoiMappingUpsertRequest, session: Session = Depends(get_session)):
    svc = PoiMappingService(session)
    row = svc.upsert(payload.kind, payload.ref, payload.poi_id, payload.area_id, payload.label)

    publish_event_nowait("poi_mapping.updated", {
        "kind": row.kind,
        "ref": row.ref,
        "poi_id": row.poi_id,
        "label": row.label,
    }, source="poi-mapping")

    return PoiMappingRead(kind=row.kind, ref=row.ref, poi_id=row.poi_id, area_id=row.area_id, label=row.label)


@router.delete("/mappings/{kind}/{ref}")
def delete_mapping(kind: str, ref: str, session: Session = Depends(get_session)):
    svc = PoiMappingService(session)
    ok = svc.delete(kind, ref)
    if not ok:
        raise HTTPException(status_code=404, detail="Mapping not found")

    publish_event_nowait("poi_mapping.deleted", {"kind": kind.upper(), "ref": ref}, source="poi-mapping")
    return {"ok": True}


@router.post("/auto-map")
async def auto_map(payload: AutoMapRequest, session: Session = Depends(get_session), robot_api: RobotAPIService = Depends(get_robot_api_service)):
    svc = PoiMappingService(session)
    res = await svc.auto_map_from_pois(robot_api, payload.robot_id, payload.table_count, payload.ref_prefix)

    publish_event_nowait("poi_mapping.auto_mapped", {
        "robot_id": payload.robot_id,
        "table_count": payload.table_count,
        **res,
    }, source="poi-mapping")

    return {"ok": True, **res}
