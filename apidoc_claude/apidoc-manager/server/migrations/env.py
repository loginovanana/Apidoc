"""Alembic env."""
from __future__ import annotations
import asyncio, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from server.models import Base

config = context.config
target_metadata = Base.metadata
DB_URL = os.environ.get("APIDOC_DB_URL",
    f"sqlite+aiosqlite:///{Path.home()/'.apidoc'/ 'data'/ 'apidoc.db'}")

def run_migrations_offline():
    context.configure(url=DB_URL, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle":"named"})
    with context.begin_transaction(): context.run_migrations()

def do_run(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction(): context.run_migrations()

async def run_async():
    cfg = config.get_section(config.config_ini_section,{}); cfg["sqlalchemy.url"] = DB_URL
    conn = async_engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with conn.connect() as c: await c.run_sync(do_run)
    await conn.dispose()

if context.is_offline_mode(): run_migrations_offline()
else: asyncio.run(run_async())
