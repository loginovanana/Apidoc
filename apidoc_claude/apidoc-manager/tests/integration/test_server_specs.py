"""Integration tests for server endpoints."""
from __future__ import annotations
import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

PAYLOAD = {
    "name": "Payment API",
    "description": "Payments",
    "content": {
        "openapi": "3.1.0",
        "info": {"title": "Payment API", "version": "1.0.0"},
        "paths": {
            "/payments": {
                "get": {"operationId": "list_payments",
                        "responses": {"200": {"description": "OK"}}},
                "post": {"operationId": "create_payment",
                         "requestBody": {"required": True, "content": {"application/json": {
                             "schema": {"type": "object", "required": ["amount"],
                                        "properties": {"amount": {"type": "number"}}}}}},
                         "responses": {"201": {"description": "Created"}}},
            }
        },
    },
}

class TestCreateSpec:
    async def test_create_201(self, async_api_client):
        r = await async_api_client.post("/specs", json=PAYLOAD)
        assert r.status_code == 201
    async def test_create_name(self, async_api_client):
        r = await async_api_client.post("/specs", json=PAYLOAD)
        assert r.json()["name"] == "Payment API"
    async def test_create_version(self, async_api_client):
        r = await async_api_client.post("/specs", json=PAYLOAD)
        assert r.json()["latest_version"] == "1.0.0"
    async def test_create_missing_name(self, async_api_client):
        r = await async_api_client.post("/specs", json={"content": {}})
        assert r.status_code == 422
    async def test_create_missing_content(self, async_api_client):
        r = await async_api_client.post("/specs", json={"name": "T"})
        assert r.status_code == 422
    async def test_create_assigns_id(self, async_api_client):
        r = await async_api_client.post("/specs", json=PAYLOAD)
        assert r.json()["id"] > 0

class TestListSpecs:
    async def test_list_200(self, async_api_client):
        r = await async_api_client.get("/specs")
        assert r.status_code == 200
    async def test_list_has_items(self, async_api_client):
        assert "items" in (await async_api_client.get("/specs")).json()
    async def test_list_pagination_fields(self, async_api_client):
        data = (await async_api_client.get("/specs")).json()
        for k in ("total","page","limit","pages"): assert k in data
    async def test_list_invalid_page(self, async_api_client):
        r = await async_api_client.get("/specs?page=0")
        assert r.status_code == 422

class TestGetSpec:
    async def test_get_200(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        spec_id = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{spec_id}")
        assert r.status_code == 200
    async def test_get_correct_name(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        spec_id = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{spec_id}")
        assert r.json()["name"] == "Payment API"
    async def test_get_includes_content(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        spec_id = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{spec_id}")
        assert r.json()["content"] is not None
    async def test_get_404(self, async_api_client):
        r = await async_api_client.get("/specs/999999")
        assert r.status_code == 404

class TestDeleteSpec:
    async def test_delete_200(self, async_api_client):
        cr = await async_api_client.post("/specs", json={**PAYLOAD, "name":"To Delete"})
        r = await async_api_client.delete(f"/specs/{cr.json()['id']}")
        assert r.status_code == 200
    async def test_delete_removes(self, async_api_client):
        cr = await async_api_client.post("/specs", json={**PAYLOAD, "name":"Temp"})
        spec_id = cr.json()["id"]
        await async_api_client.delete(f"/specs/{spec_id}")
        assert (await async_api_client.get(f"/specs/{spec_id}")).status_code == 404
    async def test_delete_404(self, async_api_client):
        r = await async_api_client.delete("/specs/999999")
        assert r.status_code == 404
    async def test_double_delete_404(self, async_api_client):
        cr = await async_api_client.post("/specs", json={**PAYLOAD, "name":"DD"})
        sid = cr.json()["id"]
        await async_api_client.delete(f"/specs/{sid}")
        assert (await async_api_client.delete(f"/specs/{sid}")).status_code == 404

class TestSearchSpecs:
    async def test_search_200(self, async_api_client):
        await async_api_client.post("/specs", json={**PAYLOAD,"name":"SearchableUniqueXYZ"})
        r = await async_api_client.get("/specs/search?q=SearchableUniqueXYZ")
        assert r.status_code == 200
    async def test_search_finds(self, async_api_client):
        await async_api_client.post("/specs", json={**PAYLOAD,"name":"FindableABC123"})
        r = await async_api_client.get("/specs/search?q=FindableABC123")
        assert r.json()["total"] >= 1
    async def test_search_no_match(self, async_api_client):
        r = await async_api_client.get("/specs/search?q=zzz999noexist")
        assert r.json()["total"] == 0
    async def test_search_no_query(self, async_api_client):
        r = await async_api_client.get("/specs/search")
        assert r.status_code == 422

class TestExportSpec:
    async def test_export_json(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{sid}/export?format=json")
        assert r.status_code == 200 and "openapi" in json.loads(r.text)
    async def test_export_yaml(self, async_api_client):
        import yaml
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{sid}/export?format=yaml")
        assert r.status_code == 200 and "openapi" in yaml.safe_load(r.text)
    async def test_export_invalid_format(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{sid}/export?format=xml")
        assert r.status_code == 422
    async def test_export_404(self, async_api_client):
        r = await async_api_client.get("/specs/999999/export?format=json")
        assert r.status_code == 404

class TestVersions:
    async def test_list_versions_200(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{sid}/versions")
        assert r.status_code == 200
    async def test_initial_version_exists(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{sid}/versions")
        assert r.json()["total"] >= 1
        assert r.json()["items"][0]["version"] == "1.0.0"
    async def test_create_version_201(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        v2c = {**PAYLOAD["content"], "info": {"title": "P", "version": "2.0.0"}}
        r = await async_api_client.post(f"/specs/{sid}/versions",
            json={"version":"2.0.0","content":v2c,"changelog":"v2"})
        assert r.status_code == 201 and r.json()["version"] == "2.0.0"
    async def test_create_version_nonexistent(self, async_api_client):
        r = await async_api_client.post("/specs/999999/versions",
            json={"version":"1.0","content":PAYLOAD["content"],"changelog":""})
        assert r.status_code == 404
    async def test_get_specific_version(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{sid}/versions/1.0.0")
        assert r.status_code == 200 and r.json()["version"] == "1.0.0"
    async def test_get_missing_version(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.get(f"/specs/{sid}/versions/99.0.0")
        assert r.status_code == 404

class TestDiffEndpoint:
    async def test_diff_same_version(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.post(f"/specs/{sid}/diff",
            json={"version1":"1.0.0","version2":"1.0.0"})
        assert r.status_code == 200 and r.json()["summary"]["total"] == 0
    async def test_diff_breaking(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        v2c = {"openapi":"3.1.0","info":{"title":"P","version":"2.0.0"},
               "paths":{"/payments":{"get":{"operationId":"list","responses":{"200":{"description":"OK"}}}}}}
        await async_api_client.post(f"/specs/{sid}/versions",
            json={"version":"2.0.0","content":v2c,"changelog":"break"})
        r = await async_api_client.post(f"/specs/{sid}/diff",
            json={"version1":"1.0.0","version2":"2.0.0"})
        assert r.status_code == 200 and r.json()["summary"]["breaking"] > 0
    async def test_diff_missing_version(self, async_api_client):
        cr = await async_api_client.post("/specs", json=PAYLOAD)
        sid = cr.json()["id"]
        r = await async_api_client.post(f"/specs/{sid}/diff",
            json={"version1":"1.0.0","version2":"99.0.0"})
        assert r.status_code == 404

class TestHealthEndpoints:
    async def test_health(self, async_api_client):
        r = await async_api_client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"
    async def test_health_db(self, async_api_client):
        r = await async_api_client.get("/health/db")
        assert r.status_code == 200
    async def test_info(self, async_api_client):
        r = await async_api_client.get("/info")
        assert r.status_code == 200 and "version" in r.json() and "specs_count" in r.json()
