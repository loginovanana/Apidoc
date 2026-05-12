"""Specification API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import Specification, SpecVersion

router = APIRouter()


@router.post("/specs", response_model=schemas.SpecificationResponse)
async def create_specification(spec_data: schemas.SpecificationCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Specification).where(Specification.name == spec_data.name))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Specification '{spec_data.name}' already exists")
        
        spec = Specification(
            name=spec_data.name,
            title=spec_data.content.get("info", {}).get("title", spec_data.name),
            description=spec_data.content.get("info", {}).get("description"),
            version=spec_data.content.get("info", {}).get("version", "1.0.0"),
            tags=spec_data.tags or [],
        )
        db.add(spec)
        await db.flush()
        
        version = SpecVersion(spec_id=spec.id, version=spec.version, content=spec_data.content, format=spec_data.format, changelog=spec_data.changelog, created_by=spec_data.created_by)
        db.add(version)
        await db.commit()
        await db.refresh(spec)
        logger.info(f"Created specification '{spec.name}' (ID: {spec.id})")
        return spec
    except HTTPException:
        raise
    except (IntegrityError, SQLAlchemyError) as e:
        await db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")


@router.get("/specs", response_model=schemas.SpecificationListResponse)
async def list_specifications(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), tag: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(Specification)
    if tag:
        query = query.where(Specification.tags.contains([tag]))
    
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    query = query.order_by(Specification.updated_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    specs = result.scalars().all()
    return {"items": specs, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}


@router.get("/specs/{spec_id}", response_model=schemas.SpecificationDetailResponse)
async def get_specification(spec_id: int, version: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    spec = result.scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    if version:
        version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
    else:
        version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).limit(1))
    spec_version = version_result.scalar_one_or_none()
    if not spec_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    
    return {**spec.__dict__, "content": spec_version.content, "format": spec_version.format}


@router.delete("/specs/{spec_id}")
async def delete_specification(spec_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    spec = result.scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    await db.delete(spec)
    await db.commit()
    logger.info(f"Deleted specification {spec_id}")
    return {"message": f"Specification {spec_id} deleted"}
