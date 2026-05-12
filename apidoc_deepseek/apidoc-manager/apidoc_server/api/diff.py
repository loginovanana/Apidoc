"""Diff API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import SpecVersion
from apidoc_server.services.diff_service import DiffService

router = APIRouter()
diff_service = DiffService()


@router.post("/specs/{spec_id}/diff")
async def compare_versions(spec_id: int, diff_request: schemas.DiffRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version.in_([diff_request.version1, diff_request.version2])))
    versions = result.scalars().all()
    if len(versions) != 2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both versions not found")
    
    v1 = next((v for v in versions if v.version == diff_request.version1), None)
    v2 = next((v for v in versions if v.version == diff_request.version2), None)
    if not v1 or not v2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versions not found")
    
    diff_result = diff_service.compare(v1.content, v2.content)
    return {"spec_id": spec_id, "version1": diff_request.version1, "version2": diff_request.version2, "changes": diff_result["changes"], "breaking_changes": diff_result["breaking_changes"], "summary": diff_result["summary"]}
