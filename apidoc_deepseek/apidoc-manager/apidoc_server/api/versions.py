"""Version management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import Specification, SpecVersion

router = APIRouter()


@router.post("/specs/{spec_id}/versions", response_model=schemas.VersionResponse)
async def create_version(spec_id: int, version_data: schemas.VersionCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    spec = result.scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version_data.version))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Version '{version_data.version}' already exists")
    
    version = SpecVersion(spec_id=spec_id, version=version_data.version, content=version_data.content, format=version_data.format, changelog=version_data.changelog, created_by=version_data.created_by)
    db.add(version)
    spec.version = version_data.version
    spec.updated_at = func.now()
    await db.commit()
    await db.refresh(version)
    return version


@router.get("/specs/{spec_id}/versions", response_model=schemas.VersionListResponse)
async def list_versions(spec_id: int, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    count_result = await db.execute(select(func.count()).select_from(SpecVersion).where(SpecVersion.spec_id == spec_id))
    total = count_result.scalar()
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    versions = result.scalars().all()
    return {"items": versions, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}


@router.get("/specs/{spec_id}/versions/{version}")
async def get_version(spec_id: int, version: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
    version_obj = result.scalar_one_or_none()
    if not version_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Version '{version}' not found")
    return version_obj


@router.delete("/specs/{spec_id}/versions/{version}")
async def delete_version(spec_id: int, version: str, db: AsyncSession = Depends(get_db)):
    count_result = await db.execute(select(func.count()).select_from(SpecVersion).where(SpecVersion.spec_id == spec_id))
    if count_result.scalar() <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the only version")
    
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
    version_obj = result.scalar_one_or_none()
    if not version_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Version '{version}' not found")
    await db.delete(version_obj)
    await db.commit()
    return {"message": f"Version '{version}' deleted"}
