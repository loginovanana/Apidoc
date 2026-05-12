"""Search API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import Specification

router = APIRouter()


@router.get("/specs/search")
async def search_specifications(q: str = Query(..., min_length=1), page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), tag: str = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(Specification).where(or_(Specification.name.ilike(f"%{q}%"), Specification.title.ilike(f"%{q}%"), Specification.description.ilike(f"%{q}%")))
    if tag:
        query = query.where(Specification.tags.contains([tag]))
    
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    result = await db.execute(query.order_by(Specification.updated_at.desc()).offset((page - 1) * per_page).limit(per_page))
    specs = result.scalars().all()
    return schemas.SpecificationListResponse(items=specs, total=total, page=page, per_page=per_page, pages=(total + per_page - 1) // per_page)
