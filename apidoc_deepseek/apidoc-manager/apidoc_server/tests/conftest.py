"""Pytest fixtures for server tests."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apidoc_server.database import Base, get_db
from apidoc_server.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield async_session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db) -> AsyncGenerator:
    async def override_get_db():
        async with test_db() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def sample_spec() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0", "description": "Test description"},
        "paths": {
            "/users": {
                "get": {"summary": "Get users", "operationId": "getUsers", "responses": {"200": {"description": "OK"}}},
                "post": {"summary": "Create user", "operationId": "createUser", "responses": {"201": {"description": "Created"}}}
            }
        }
    }
