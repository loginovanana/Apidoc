"""Security tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    responses = []
    for _ in range(70):
        resp = await client.get("/health")
        responses.append(resp)
    assert any(r.status_code == 429 for r in responses)


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    response = await client.options("/api/v1/specs", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_id_header(client: AsyncClient):
    response = await client.get("/health")
    assert "X-Request-ID" in response.headers
