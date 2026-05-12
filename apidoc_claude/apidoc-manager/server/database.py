"""Async SQLAlchemy engine and session."""
from __future__ import annotations
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_data_dir = Path.home() / ".apidoc" / "data"; _data_dir.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.environ.get("APIDOC_DB_URL", f"sqlite+aiosqlite:///{_data_dir / 'apidoc.db'}")

engine = create_async_engine(DATABASE_URL, echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def create_tables() -> None:
    from server.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
