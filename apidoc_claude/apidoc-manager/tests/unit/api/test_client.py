"""Unit tests for ServerClient (mocked HTTP)."""
from __future__ import annotations
from unittest.mock import patch
import pytest, respx
from httpx import Response
from apidoc.api.client import ServerClient
from apidoc.utils.errors import AuthError, NetworkError, NotFoundError, ServerError

BASE = "http://localhost:8000"
def mk(): return ServerClient(base_url=BASE, timeout=5)

SPEC = {"id":42,"name":"Test","description":"","latest_version":"1.0.0",
        "versions_count":1,"created_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-01T00:00:00Z"}

class TestServerClient:
    @respx.mock
    def test_health_ok(self):
        respx.get(f"{BASE}/health").mock(return_value=Response(200,json={"status":"ok"}))
        assert mk().health()["status"] == "ok"
    @respx.mock
    def test_network_error(self):
        import httpx
        respx.get(f"{BASE}/health").mock(side_effect=httpx.ConnectError("refused"))
        with pytest.raises(NetworkError): mk().health()
    @respx.mock
    def test_list_specs(self):
        respx.get(f"{BASE}/specs").mock(return_value=Response(200,json={"items":[],"total":0,"page":1,"limit":20,"pages":1}))
        assert "items" in mk().list_specs()
    @respx.mock
    def test_get_spec(self):
        respx.get(f"{BASE}/specs/42").mock(return_value=Response(200,json=SPEC))
        assert mk().get_spec(42)["id"] == 42
    @respx.mock
    def test_get_spec_404(self):
        respx.get(f"{BASE}/specs/999").mock(return_value=Response(404,json={"detail":"Not found"}))
        with pytest.raises(NotFoundError): mk().get_spec(999)
    @respx.mock
    def test_create_spec(self):
        respx.post(f"{BASE}/specs").mock(return_value=Response(201,json=SPEC))
        assert mk().create_spec("Test",{},"")["id"] == 42
    @respx.mock
    def test_delete_spec(self):
        respx.delete(f"{BASE}/specs/5").mock(return_value=Response(200,json={"deleted":5,"status":"ok"}))
        assert mk().delete_spec(5)["deleted"] == 5
    @respx.mock
    def test_500_raises(self):
        respx.get(f"{BASE}/specs").mock(return_value=Response(500,text="err"))
        with pytest.raises(ServerError): mk().list_specs()
    @respx.mock
    def test_401_raises(self):
        respx.get(f"{BASE}/specs/1").mock(return_value=Response(401,json={"detail":"Unauthorized"}))
        with pytest.raises(AuthError): mk().get_spec(1)
    @respx.mock
    def test_search(self):
        respx.get(f"{BASE}/specs/search").mock(return_value=Response(200,json={"items":[SPEC],"total":1,"page":1,"limit":10,"pages":1}))
        assert len(mk().search_specs("test")["items"]) == 1
