"""Version service."""

import re
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server.models import Specification, SpecVersion
from apidoc_server.services.validation_service import ValidationService


class VersionService:
    def __init__(self):
        self.validator = ValidationService()
    
    async def create_version(self, db: AsyncSession, spec_id: int, version: str, content: Dict[str, Any], format: str = "json", changelog: Optional[str] = None, created_by: Optional[str] = None) -> SpecVersion:
        validation_result = await self.validator.validate(content)
        if not validation_result["valid"]:
            raise ValueError(f"Invalid specification: {validation_result['errors']}")
        
        result = await db.execute(select(Specification).where(Specification.id == spec_id))
        spec = result.scalar_one_or_none()
        if not spec: raise ValueError(f"Specification {spec_id} not found")
        
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
        if result.scalar_one_or_none(): raise ValueError(f"Version '{version}' already exists")
        
        new_version = SpecVersion(spec_id=spec_id, version=version, content=content, format=format, changelog=changelog, created_by=created_by)
        db.add(new_version)
        spec.version = version
        await db.commit()
        await db.refresh(new_version)
        logger.info(f"Created version '{version}' for specification {spec_id}")
        return new_version
    
    async def get_version(self, db: AsyncSession, spec_id: int, version: str) -> Optional[SpecVersion]:
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
        return result.scalar_one_or_none()
    
    async def get_latest_version(self, db: AsyncSession, spec_id: int) -> Optional[SpecVersion]:
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).limit(1))
        return result.scalar_one_or_none()
    
    async def list_versions(self, db: AsyncSession, spec_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        count_result = await db.execute(select(func.count()).select_from(SpecVersion).where(SpecVersion.spec_id == spec_id))
        total = count_result.scalar()
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
        items = result.scalars().all()
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}
    
    async def delete_version(self, db: AsyncSession, spec_id: int, version: str) -> bool:
        count_result = await db.execute(select(func.count()).select_from(SpecVersion).where(SpecVersion.spec_id == spec_id))
        if count_result.scalar() <= 1: raise ValueError("Cannot delete the only version")
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
        version_obj = result.scalar_one_or_none()
        if not version_obj: return False
        await db.delete(version_obj)
        spec_result = await db.execute(select(Specification).where(Specification.id == spec_id))
        spec = spec_result.scalar_one()
        if spec.version == version:
            latest = await self.get_latest_version(db, spec_id)
            if latest: spec.version = latest.version
        await db.commit()
        return True
    
    def _increment_version(self, version: str) -> str:
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
        if match:
            major, minor, patch = map(int, match.groups())
            return f"{major}.{minor}.{patch + 1}"
        return f"{version}.1"
