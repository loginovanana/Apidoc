"""Business logic for specs and versions."""
from __future__ import annotations
import json, math
from typing import Any
import httpx, yaml
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from server.models import Spec, SpecVersion
from server.schemas import SpecCreate, SpecListResponse, SpecResponse, SpecVersionCreate

def _to_response(spec: Spec, with_content: bool = False) -> SpecResponse:
    content = spec.versions[0].get_content() if (with_content and spec.versions) else None
    return SpecResponse(id=spec.id, name=spec.name, description=spec.description,
                        latest_version=spec.latest_version, versions_count=len(spec.versions),
                        created_at=spec.created_at, updated_at=spec.updated_at, content=content)

async def _get_loaded(db: AsyncSession, spec_id: int) -> Spec | None:
    result = await db.execute(
        select(Spec).options(selectinload(Spec.versions)).where(Spec.id == spec_id))
    return result.scalar_one_or_none()

async def create_spec(db: AsyncSession, data: SpecCreate) -> Spec:
    spec = Spec(name=data.name, description=data.description, latest_version="")
    db.add(spec); await db.flush()
    ver_str = data.content.get("info", {}).get("version", "1.0.0")
    sv = SpecVersion(spec_id=spec.id, version=ver_str,
                     content=json.dumps(data.content, ensure_ascii=False),
                     content_hash=SpecVersion.compute_hash(data.content), changelog="Initial version")
    db.add(sv); spec.latest_version = ver_str
    await db.commit(); await db.refresh(spec)
    return await _get_loaded(db, spec.id)

async def list_specs(db: AsyncSession, page: int, limit: int) -> SpecListResponse:
    total = (await db.execute(select(func.count()).select_from(Spec))).scalar_one()
    result = await db.execute(
        select(Spec).options(selectinload(Spec.versions))
        .offset((page-1)*limit).limit(limit).order_by(Spec.updated_at.desc()))
    specs = result.scalars().all()
    return SpecListResponse(items=[_to_response(s) for s in specs], total=total,
                            page=page, limit=limit, pages=max(1, math.ceil(total/limit)))

async def get_spec(db: AsyncSession, spec_id: int) -> Spec | None:
    return await _get_loaded(db, spec_id)

async def delete_spec(db: AsyncSession, spec_id: int) -> bool:
    spec = await _get_loaded(db, spec_id)
    if not spec: return False
    await db.delete(spec); await db.commit(); return True

async def search_specs(db: AsyncSession, query: str, page: int, limit: int) -> SpecListResponse:
    q = f"%{query}%"
    where = or_(Spec.name.ilike(q), Spec.description.ilike(q))
    total = (await db.execute(select(func.count()).select_from(Spec).where(where))).scalar_one()
    result = await db.execute(
        select(Spec).options(selectinload(Spec.versions)).where(where)
        .offset((page-1)*limit).limit(limit).order_by(Spec.updated_at.desc()))
    specs = result.scalars().all()
    return SpecListResponse(items=[_to_response(s) for s in specs], total=total,
                            page=page, limit=limit, pages=max(1, math.ceil(total/limit)))

async def import_from_url(db: AsyncSession, url: str) -> Spec:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, follow_redirects=True); r.raise_for_status()
    ct = r.headers.get("content-type","")
    content = r.json() if ("json" in ct or url.endswith(".json")) else yaml.safe_load(r.text)
    name = content.get("info",{}).get("title", url.split("/")[-1])
    return await create_spec(db, SpecCreate(name=name, content=content))

async def get_versions(db: AsyncSession, spec_id: int) -> list[SpecVersion]:
    result = await db.execute(
        select(SpecVersion).where(SpecVersion.spec_id==spec_id)
        .order_by(SpecVersion.created_at.desc()))
    return result.scalars().all()

async def create_version(db: AsyncSession, spec_id: int, data: SpecVersionCreate) -> SpecVersion | None:
    spec = await _get_loaded(db, spec_id)
    if not spec: return None
    sv = SpecVersion(spec_id=spec_id, version=data.version,
                     content=json.dumps(data.content, ensure_ascii=False),
                     content_hash=SpecVersion.compute_hash(data.content), changelog=data.changelog)
    db.add(sv); spec.latest_version = data.version
    await db.commit(); await db.refresh(sv); return sv

async def diff_versions(db: AsyncSession, spec_id: int, v1: str, v2: str) -> dict[str, Any]:
    from apidoc.commands.diff import _compare_specs
    result = await db.execute(
        select(SpecVersion).where(SpecVersion.spec_id==spec_id, SpecVersion.version.in_([v1,v2])))
    versions = {sv.version: sv for sv in result.scalars().all()}
    missing = [v for v in [v1,v2] if v not in versions]
    if missing: raise ValueError(f"Version(s) not found: {missing}")
    return _compare_specs(versions[v1].get_content(), versions[v2].get_content())
