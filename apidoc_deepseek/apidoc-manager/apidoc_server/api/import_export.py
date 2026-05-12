"""Import/Export API endpoints."""

import json
from typing import Optional

import httpx
import yaml
from fastapi import APIRouter, Depends, HTTPException, Response, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import Specification, SpecVersion

router = APIRouter()


@router.post("/specs/import")
async def import_specification(import_data: schemas.SpecificationImport, db: AsyncSession = Depends(get_db)):
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(str(import_data.url))
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            
            if "json" in content_type:
                content = response.json()
                format_type = "json"
            elif "yaml" in content_type:
                content = yaml.safe_load(response.text)
                format_type = "yaml"
            else:
                try:
                    content = response.json()
                    format_type = "json"
                except Exception:
                    content = yaml.safe_load(response.text)
                    format_type = "yaml"
            
            info = content.get("info", {})
            spec_name = import_data.name or info.get("title", "Imported API")
            
            spec = Specification(name=spec_name, title=info.get("title", spec_name), description=info.get("description"), version=info.get("version", "1.0.0"), tags=import_data.tags or [])
            db.add(spec)
            await db.flush()
            
            version = SpecVersion(spec_id=spec.id, version=spec.version, content=content, format=format_type, changelog=f"Imported from {import_data.url}", created_by=import_data.created_by)
            db.add(version)
            await db.commit()
            await db.refresh(spec)
            logger.info(f"Imported specification from {import_data.url} (ID: {spec.id})")
            return spec
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch URL: {str(e)}")


@router.get("/specs/{spec_id}/export")
async def export_specification(spec_id: int, format: str = "json", version: Optional[str] = None, db: AsyncSession = Depends(get_db)):
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
    
    content = spec_version.content
    if format == "json":
        return Response(content=json.dumps(content, indent=2, ensure_ascii=False), media_type="application/json", headers={"Content-Disposition": f'attachment; filename="{spec.name}.json"'})
    elif format == "yaml":
        return Response(content=yaml.safe_dump(content, sort_keys=False, allow_unicode=True), media_type="application/yaml", headers={"Content-Disposition": f'attachment; filename="{spec.name}.yaml"'})
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format: {format}")
