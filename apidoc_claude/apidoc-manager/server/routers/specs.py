"""Spec API router — all /specs endpoints."""
from __future__ import annotations
import json
import yaml
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from server.database import get_db
from server.schemas import DiffRequest, ImportRequest, SpecCreate, SpecListResponse, SpecResponse, SpecVersionCreate
from server.services import spec_service

router = APIRouter(prefix="/specs", tags=["specs"])

def _404(spec_id: int):
    raise HTTPException(404, detail=f"Spec {spec_id} not found")

def _detail(spec) -> SpecResponse:
    content = spec.versions[0].get_content() if spec.versions else None
    return SpecResponse(id=spec.id, name=spec.name, description=spec.description,
                        latest_version=spec.latest_version, versions_count=len(spec.versions),
                        created_at=spec.created_at, updated_at=spec.updated_at, content=content)

@router.post("", response_model=SpecResponse, status_code=201)
async def create_spec(data: SpecCreate, db: AsyncSession = Depends(get_db)):
    """Upload a new OpenAPI specification."""
    spec = await spec_service.create_spec(db, data)
    return _detail(spec)

@router.get("", response_model=SpecListResponse)
async def list_specs(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
                     db: AsyncSession = Depends(get_db)):
    """List specifications with pagination."""
    return await spec_service.list_specs(db, page=page, limit=limit)

@router.get("/search", response_model=SpecListResponse)
async def search_specs(q: str = Query(..., min_length=1), page: int = Query(1, ge=1),
                       limit: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    """Search by name or description."""
    return await spec_service.search_specs(db, query=q, page=page, limit=limit)

@router.post("/import", response_model=SpecResponse, status_code=201)
async def import_spec(data: ImportRequest, db: AsyncSession = Depends(get_db)):
    """Import a specification from an external URL."""
    try:
        spec = await spec_service.import_from_url(db, data.url)
    except Exception as exc:
        raise HTTPException(422, detail=f"Import failed: {exc}")
    return _detail(spec)

@router.get("/{spec_id}", response_model=SpecResponse)
async def get_spec(spec_id: int, db: AsyncSession = Depends(get_db)):
    """Get specification by ID (includes content)."""
    spec = await spec_service.get_spec(db, spec_id)
    if not spec: _404(spec_id)
    return _detail(spec)

@router.delete("/{spec_id}")
async def delete_spec(spec_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a specification."""
    if not await spec_service.delete_spec(db, spec_id): _404(spec_id)
    return {"deleted": spec_id, "status": "ok"}

@router.get("/{spec_id}/export")
async def export_spec(spec_id: int, format: str = Query("yaml", pattern="^(yaml|json)$"),
                      db: AsyncSession = Depends(get_db)):
    """Export as YAML or JSON."""
    spec = await spec_service.get_spec(db, spec_id)
    if not spec: _404(spec_id)
    if not spec.versions: raise HTTPException(404, detail="No versions found")
    content = spec.versions[0].get_content()
    if format == "json":
        return Response(json.dumps(content, indent=2, ensure_ascii=False), media_type="application/json")
    return Response(yaml.dump(content, allow_unicode=True, sort_keys=False), media_type="application/yaml")

@router.get("/{spec_id}/versions")
async def list_versions(spec_id: int, db: AsyncSession = Depends(get_db)):
    """List all versions of a specification."""
    spec = await spec_service.get_spec(db, spec_id)
    if not spec: _404(spec_id)
    versions = await spec_service.get_versions(db, spec_id)
    return {"spec_id": spec_id, "total": len(versions),
            "items": [{"id":v.id,"version":v.version,"content_hash":v.content_hash,
                       "changelog":v.changelog,"created_at":v.created_at.isoformat()}
                      for v in versions]}

@router.post("/{spec_id}/versions", status_code=201)
async def create_version(spec_id: int, data: SpecVersionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new version."""
    spec = await spec_service.get_spec(db, spec_id)
    if not spec: _404(spec_id)
    sv = await spec_service.create_version(db, spec_id, data)
    if not sv: _404(spec_id)
    return {"id":sv.id,"spec_id":sv.spec_id,"version":sv.version,
            "content_hash":sv.content_hash,"changelog":sv.changelog,"created_at":sv.created_at.isoformat()}

@router.get("/{spec_id}/versions/{version}")
async def get_version(spec_id: int, version: str, db: AsyncSession = Depends(get_db)):
    """Get a specific version."""
    from sqlalchemy import select; from server.models import SpecVersion
    result = await db.execute(
        select(SpecVersion).where(SpecVersion.spec_id==spec_id, SpecVersion.version==version))
    sv = result.scalar_one_or_none()
    if not sv: raise HTTPException(404, detail=f"Version '{version}' not found")
    return {"id":sv.id,"spec_id":sv.spec_id,"version":sv.version,"content":sv.get_content(),
            "content_hash":sv.content_hash,"changelog":sv.changelog,"created_at":sv.created_at.isoformat()}

@router.post("/{spec_id}/diff")
async def diff_versions(spec_id: int, data: DiffRequest, db: AsyncSession = Depends(get_db)):
    """Compare two versions."""
    spec = await spec_service.get_spec(db, spec_id)
    if not spec: _404(spec_id)
    try:
        return await spec_service.diff_versions(db, spec_id, data.version1, data.version2)
    except ValueError as exc:
        raise HTTPException(404, detail=str(exc))
