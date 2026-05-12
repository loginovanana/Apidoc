"""Shared test fixtures."""
from __future__ import annotations
import asyncio, json
from pathlib import Path
from typing import AsyncGenerator, Generator
import pytest, pytest_asyncio, yaml
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from server.database import get_db
from server.main import app as fastapi_app
from server.models import Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session: yield session

app_instance = fastapi_app
app_instance.dependency_overrides[get_db] = override_get_db

SAMPLE_SPEC: dict = {
    "openapi": "3.1.0",
    "info": {"title": "Test API", "version": "1.0.0"},
    "paths": {
        "/users": {
            "get":  {"operationId":"list_users","summary":"List users",
                     "responses":{"200":{"description":"OK"}}},
            "post": {"operationId":"create_user","summary":"Create user",
                     "requestBody":{"required":True,"content":{"application/json":{
                         "schema":{"type":"object","required":["name"],
                                   "properties":{"name":{"type":"string"}}}}}},
                     "responses":{"201":{"description":"Created"}}},
        },
        "/users/{id}": {
            "get": {"operationId":"get_user","summary":"Get user",
                    "parameters":[{"name":"id","in":"path","required":True,"schema":{"type":"integer"}}],
                    "responses":{"200":{"description":"OK"},"404":{"description":"Not found"}}},
            "delete": {"operationId":"delete_user","summary":"Delete user",
                       "parameters":[{"name":"id","in":"path","required":True,"schema":{"type":"integer"}}],
                       "responses":{"204":{"description":"Deleted"}}},
        },
    },
}

SAMPLE_SPEC_V2: dict = {
    "openapi": "3.1.0",
    "info": {"title": "Test API", "version": "2.0.0"},
    "paths": {
        "/users": {
            "get": {"operationId":"list_users","summary":"List all users",
                    "responses":{"200":{"description":"OK"}}},
        },
        "/users/{id}": {
            "get": {"operationId":"get_user","summary":"Get user",
                    "parameters":[{"name":"id","in":"path","required":True,"schema":{"type":"integer"}}],
                    "responses":{"200":{"description":"OK"}}},
            "delete": {"operationId":"delete_user","summary":"Delete user",
                       "parameters":[{"name":"id","in":"path","required":True,"schema":{"type":"integer"}}],
                       "responses":{"204":{"description":"Deleted"}}},
        },
        "/users/bulk": {
            "post": {"operationId":"bulk_create","summary":"Bulk create",
                     "responses":{"201":{"description":"Created"}}},
        },
    },
}

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop(); yield loop; loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def async_api_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app_instance),
                           base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_spec() -> dict: return dict(SAMPLE_SPEC)

@pytest.fixture
def sample_spec_v2() -> dict: return dict(SAMPLE_SPEC_V2)

@pytest.fixture
def spec_yaml_file(tmp_path: Path, sample_spec: dict) -> Path:
    p = tmp_path / "openapi.yaml"
    p.write_text(yaml.dump(sample_spec, allow_unicode=True), encoding="utf-8")
    return p

@pytest.fixture
def spec_json_file(tmp_path: Path, sample_spec: dict) -> Path:
    p = tmp_path / "openapi.json"
    p.write_text(json.dumps(sample_spec, indent=2), encoding="utf-8")
    return p
