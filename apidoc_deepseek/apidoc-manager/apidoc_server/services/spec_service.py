"""Specification service."""

from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server.models import Specification, SpecVersion
from apidoc_server.services.validation_service import ValidationService


class SpecService:
    def __init__(self):
        self.validator = ValidationService()
    
    async def create_specification(self, db: AsyncSession, name: str, content: Dict[str, Any], format: str = "json", tags: Optional[List[str]] = None, created_by: Optional[str] = None) -> Specification:
        validation_result = await self.validator.validate(content)
        if not validation_result["valid"]:
            raise ValueError(f"Invalid specification: {validation_result['errors']}")
        
        info = content.get("info", {})
        spec = Specification(name=name, title=info.get("title", name), description=info.get("description"), version=info.get("version", "1.0.0"), tags=tags or [])
        db.add(spec)
        await db.flush()
        
        version = SpecVersion(spec_id=spec.id, version=spec.version, content=content, format=format, created_by=created_by, changelog="Initial version")
        db.add(version)
        await db.commit()
        await db.refresh(spec)
        logger.info(f"Created specification '{name}' (ID: {spec.id})")
        return spec
    
    async def get_specification(self, db: AsyncSession, spec_id: int, include_content: bool = True) -> Optional[Dict[str, Any]]:
        result = await db.execute(select(Specification).where(Specification.id == spec_id))
        spec = result.scalar_one_or_none()
        if not spec: return None
        data = spec.__dict__.copy()
        if include_content:
            version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).limit(1))
            version = version_result.scalar_one_or_none()
            if version: data["content"] = version.content; data["format"] = version.format
        return data
    
    async def list_specifications(self, db: AsyncSession, page: int = 1, per_page: int = 20, tag: Optional[str] = None) -> Dict[str, Any]:
        query = select(Specification)
        if tag: query = query.where(Specification.tags.contains([tag]))
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar()
        query = query.order_by(Specification.updated_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        items = result.scalars().all()
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}
    
    async def delete_specification(self, db: AsyncSession, spec_id: int) -> bool:
        result = await db.execute(select(Specification).where(Specification.id == spec_id))
        spec = result.scalar_one_or_none()
        if not spec: return False
        await db.delete(spec)
        await db.commit()
        logger.info(f"Deleted specification {spec_id}")
        return True
    
    async def search_specifications(self, db: AsyncSession, query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        search_query = select(Specification).where(or_(Specification.name.ilike(f"%{query}%"), Specification.title.ilike(f"%{query}%"), Specification.description.ilike(f"%{query}%")))
        count_result = await db.execute(select(func.count()).select_from(search_query.subquery()))
        total = count_result.scalar()
        search_query = search_query.order_by(Specification.updated_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(search_query)
        items = result.scalars().all()
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}
