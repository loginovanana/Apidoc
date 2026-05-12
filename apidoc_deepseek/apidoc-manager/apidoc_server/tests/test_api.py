"""API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_specification(client: AsyncClient, sample_spec):
    response = await client.post("/api/v1/specs", json={"name": "test-api", "content": sample_spec, "format": "json"})
    assert response.status_code == 200
    assert response.json()["name"] == "test-api"


@pytest.mark.asyncio
async def test_create_duplicate_specification(client: AsyncClient, sample_spec):
    await client.post("/api/v1/specs", json={"name": "duplicate-api", "content": sample_spec, "format": "json"})
    response = await client.post("/api/v1/specs", json={"name": "duplicate-api", "content": sample_spec, "format": "json"})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_specification(client: AsyncClient, sample_spec):
    create_resp = await client.post("/api/v1/specs", json={"name": "get-test", "content": sample_spec, "format": "json"})
    spec_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/specs/{spec_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_nonexistent_specification(client: AsyncClient):
    response = await client.get("/api/v1/specs/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_specifications(client: AsyncClient, sample_spec):
    for i in range(3):
        await client.post("/api/v1/specs", json={"name": f"list-test-{i}", "content": sample_spec, "format": "json"})
    response = await client.get("/api/v1/specs")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 3


@pytest.mark.asyncio
async def test_search_specifications(client: AsyncClient, sample_spec):
    await client.post("/api/v1/specs", json={"name": "payment-api", "content": sample_spec, "format": "json"})
    await client.post("/api/v1/specs", json={"name": "user-api", "content": sample_spec, "format": "json"})
    response = await client.get("/api/v1/specs/search?q=payment")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


@pytest.mark.asyncio
async def test_delete_specification(client: AsyncClient, sample_spec):
    create_resp = await client.post("/api/v1/specs", json={"name": "delete-test", "content": sample_spec, "format": "json"})
    spec_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/specs/{spec_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_version(client: AsyncClient, sample_spec):
    create_resp = await client.post("/api/v1/specs", json={"name": "version-test", "content": sample_spec, "format": "json"})
    spec_id = create_resp.json()["id"]
    sample_spec["info"]["version"] = "2.0.0"
    response = await client.post(f"/api/v1/specs/{spec_id}/versions", json={"content": sample_spec, "version": "2.0.0", "format": "json"})
    assert response.status_code == 200
