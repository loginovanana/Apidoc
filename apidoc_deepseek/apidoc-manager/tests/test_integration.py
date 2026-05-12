"""Integration tests for CLI and Server."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_spec_lifecycle(client: AsyncClient):
    spec = {"openapi": "3.0.3", "info": {"title": "Lifecycle Test", "version": "1.0.0"}, "paths": {"/items": {"get": {"summary": "List items", "operationId": "listItems", "responses": {"200": {"description": "OK"}}}}}}
    
    response = await client.post("/api/v1/specs", json={"name": "lifecycle-test", "content": spec, "format": "json"})
    assert response.status_code == 200
    spec_id = response.json()["id"]
    
    response = await client.get(f"/api/v1/specs/{spec_id}")
    assert response.status_code == 200
    
    spec["info"]["version"] = "2.0.0"
    response = await client.post(f"/api/v1/specs/{spec_id}/versions", json={"content": spec, "version": "2.0.0", "format": "json"})
    assert response.status_code == 200
    
    response = await client.get(f"/api/v1/specs/{spec_id}/versions")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    
    response = await client.post(f"/api/v1/specs/{spec_id}/diff", json={"version1": "1.0.0", "version2": "2.0.0"})
    assert response.status_code == 200
    
    response = await client.delete(f"/api/v1/specs/{spec_id}")
    assert response.status_code == 200
