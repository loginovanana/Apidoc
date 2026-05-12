"""CLI ↔ server integration tests (mocked HTTP)."""
from __future__ import annotations
import json
from unittest.mock import patch
import pytest, respx
from httpx import Response
from typer.testing import CliRunner
from apidoc.cli import app

runner = CliRunner()
BASE = "http://localhost:8000"

SPEC_R = {"id":42,"name":"Pay API","description":"","latest_version":"1.0.0",
          "versions_count":1,"created_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-01T00:00:00Z"}
LIST_R = {"items":[SPEC_R],"total":1,"page":1,"limit":20,"pages":1}

class TestServerListCmd:
    @respx.mock
    def test_shows_table(self):
        respx.get(f"{BASE}/specs").mock(return_value=Response(200,json=LIST_R))
        r = runner.invoke(app, ["server","list"])
        assert r.exit_code == 0 and "Pay API" in r.output
    @respx.mock
    def test_json_output(self):
        respx.get(f"{BASE}/specs").mock(return_value=Response(200,json=LIST_R))
        r = runner.invoke(app, ["server","list","--json"])
        assert r.exit_code == 0 and json.loads(r.output)["items"][0]["name"]=="Pay API"
    def test_offline_exits(self):
        import httpx
        with patch("apidoc.api.client.httpx.get", side_effect=httpx.ConnectError("refused")):
            r = runner.invoke(app, ["server","list"])
        assert r.exit_code != 0

class TestServerGetCmd:
    @respx.mock
    def test_get_existing(self):
        respx.get(f"{BASE}/specs/42").mock(return_value=Response(200,json={**SPEC_R,"content":None}))
        r = runner.invoke(app, ["server","get","42"])
        assert r.exit_code == 0
    @respx.mock
    def test_get_json(self):
        respx.get(f"{BASE}/specs/42").mock(return_value=Response(200,json={**SPEC_R,"content":None}))
        r = runner.invoke(app, ["server","get","42","--json"])
        assert r.exit_code == 0 and json.loads(r.output)["id"]==42
    @respx.mock
    def test_get_404(self):
        respx.get(f"{BASE}/specs/999").mock(return_value=Response(404,json={"detail":"Not found"}))
        r = runner.invoke(app, ["server","get","999"])
        assert r.exit_code != 0

class TestServerSearchCmd:
    @respx.mock
    def test_shows_results(self):
        respx.get(f"{BASE}/specs/search").mock(return_value=Response(200,json={
            "items":[SPEC_R],"total":1,"page":1,"limit":10,"pages":1}))
        r = runner.invoke(app, ["server","search","pay"])
        assert r.exit_code == 0 and "Pay API" in r.output
    @respx.mock
    def test_no_results(self):
        respx.get(f"{BASE}/specs/search").mock(return_value=Response(200,json={
            "items":[],"total":0,"page":1,"limit":10,"pages":1}))
        r = runner.invoke(app, ["server","search","nomatch"])
        assert r.exit_code == 0
    @respx.mock
    def test_json_output(self):
        respx.get(f"{BASE}/specs/search").mock(return_value=Response(200,json={
            "items":[SPEC_R],"total":1,"page":1,"limit":10,"pages":1}))
        r = runner.invoke(app, ["server","search","pay","--json"])
        assert r.exit_code == 0 and "items" in json.loads(r.output)

class TestServerVersionsCmd:
    @respx.mock
    def test_shows_history(self):
        respx.get(f"{BASE}/specs/42/versions").mock(return_value=Response(200,json={
            "spec_id":42,"total":2,"items":[
                {"id":1,"version":"1.0.0","changelog":"Init",
                 "content_hash":"abc","created_at":"2026-01-01T00:00:00Z"},
                {"id":2,"version":"1.1.0","changelog":"Fix",
                 "content_hash":"def","created_at":"2026-02-01T00:00:00Z"},
            ]}))
        r = runner.invoke(app, ["server","versions","42"])
        assert r.exit_code == 0 and "1.0.0" in r.output and "1.1.0" in r.output

class TestServerStatusCmd:
    @respx.mock
    def test_online(self):
        respx.get(f"{BASE}/health").mock(return_value=Response(200,json={"status":"ok"}))
        respx.get(f"{BASE}/info").mock(return_value=Response(200,json={
            "version":"1.0.0","db_url":"sqlite","specs_count":5}))
        r = runner.invoke(app, ["server","status"])
        assert r.exit_code == 0 and "online" in r.output.lower()
    def test_offline(self):
        import httpx
        with patch("apidoc.api.client.httpx.get", side_effect=httpx.ConnectError("refused")):
            r = runner.invoke(app, ["server","status"])
        assert r.exit_code != 0

class TestPublishCmd:
    @respx.mock
    def test_server_only(self, spec_yaml_file):
        respx.post(f"{BASE}/specs").mock(return_value=Response(201,json={**SPEC_R,"content":None}))
        respx.post(f"{BASE}/specs/42/versions").mock(return_value=Response(201,json={
            "id":1,"spec_id":42,"version":"1.0.0","content_hash":"x","changelog":"","created_at":"2026-01-01T00:00:00Z"}))
        r = runner.invoke(app, ["publish", str(spec_yaml_file), "--server-only"])
        assert r.exit_code == 0
    @respx.mock
    def test_json_output(self, spec_yaml_file):
        respx.post(f"{BASE}/specs").mock(return_value=Response(201,json={**SPEC_R,"content":None}))
        respx.post(f"{BASE}/specs/42/versions").mock(return_value=Response(201,json={
            "id":1,"spec_id":42,"version":"1.0.0","content_hash":"x","changelog":"","created_at":"2026-01-01T00:00:00Z"}))
        r = runner.invoke(app, ["publish", str(spec_yaml_file), "--server-only","--json"])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "results" in data and "summary" in data

class TestDiffWithServer:
    @respx.mock
    def test_nonbreaking_exits_0(self):
        respx.post(f"{BASE}/specs/1/diff").mock(return_value=Response(200,json={
            "breaking_changes":[],"non_breaking_changes":[
                {"type":"endpoint_added","endpoint":"GET /new","description":"New"}],
            "summary":{"total":1,"breaking":0,"non_breaking":1}}))
        r = runner.invoke(app, ["diff","--from-server","1","--version1","1.0","--version2","1.1"])
        assert r.exit_code == 0
    @respx.mock
    def test_breaking_exits_1(self):
        respx.post(f"{BASE}/specs/1/diff").mock(return_value=Response(200,json={
            "breaking_changes":[{"type":"endpoint_removed","endpoint":"DEL /x","description":"Removed"}],
            "non_breaking_changes":[],"summary":{"total":1,"breaking":1,"non_breaking":0}}))
        r = runner.invoke(app, ["diff","--from-server","1","--version1","1.0","--version2","2.0"])
        assert r.exit_code != 0
