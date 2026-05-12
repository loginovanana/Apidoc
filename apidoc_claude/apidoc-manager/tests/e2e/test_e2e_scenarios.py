"""End-to-end scenario tests."""
from __future__ import annotations
import ast, json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest, yaml
from httpx import AsyncClient
from typer.testing import CliRunner
from apidoc.cli import app

runner = CliRunner()
pytestmark = pytest.mark.asyncio

FASTAPI_SRC = """
from fastapi import FastAPI
api = FastAPI()
@api.get("/orders")
def list_orders(): return []
@api.post("/orders")
def create_order(): return {}
@api.get("/orders/{order_id}")
def get_order(order_id: int): return {}
"""

class TestE2EGenerateValidate:
    def test_generate_then_validate(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        spec_file = tmp_path/"openapi.yaml"
        r = runner.invoke(app, ["generate", str(src), "--output", str(spec_file), "--framework","fastapi"])
        assert r.exit_code == 0 and spec_file.exists()
        with patch("apidoc.api.validators.validate_external") as m:
            m.return_value = MagicMock(errors=[], warnings=[], is_valid=True)
            vr = runner.invoke(app, ["validate", str(spec_file)])
        assert vr.exit_code == 0

    async def test_generate_publish_list(self, tmp_path, async_api_client: AsyncClient):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        spec_file = tmp_path/"openapi.yaml"
        runner.invoke(app, ["generate", str(src), "--output", str(spec_file), "--framework","fastapi"])
        spec = yaml.safe_load(spec_file.read_text())
        resp = await async_api_client.post("/specs", json={"name":"E2E Orders","description":"","content":spec})
        assert resp.status_code == 201
        spec_id = resp.json()["id"]
        list_resp = await async_api_client.get("/specs")
        ids = [s["id"] for s in list_resp.json()["items"]]
        assert spec_id in ids
        get_resp = await async_api_client.get(f"/specs/{spec_id}")
        assert get_resp.json()["name"] == "E2E Orders"

class TestE2EDiffVersions:
    async def test_two_versions_diff(self, async_api_client: AsyncClient):
        v1 = {"openapi":"3.1.0","info":{"title":"T","version":"1.0.0"},"paths":{
            "/orders":{"get":{"operationId":"list","responses":{"200":{"description":"OK"}}},
                       "post":{"operationId":"create","responses":{"201":{"description":"Created"}}}}}}
        v2 = {"openapi":"3.1.0","info":{"title":"T","version":"2.0.0"},"paths":{
            "/orders":{"get":{"operationId":"list","responses":{"200":{"description":"OK"}}}}}}
        cr = await async_api_client.post("/specs", json={"name":"E2E Diff","description":"","content":v1})
        sid = cr.json()["id"]
        await async_api_client.post(f"/specs/{sid}/versions",
            json={"version":"2.0.0","content":v2,"changelog":"Breaking"})
        versions = (await async_api_client.get(f"/specs/{sid}/versions")).json()
        assert versions["total"] == 2
        diff = (await async_api_client.post(f"/specs/{sid}/diff",
            json={"version1":"1.0.0","version2":"2.0.0"})).json()
        assert diff["summary"]["breaking"] > 0

class TestE2EValidateFix:
    def test_fix_then_revalidate(self, tmp_path):
        spec = {"openapi":"3.1.0","info":{"title":"T"},"paths":{}}
        f = tmp_path/"broken.yaml"; f.write_text(yaml.dump(spec))
        with patch("apidoc.api.validators.validate_external") as m:
            m.return_value = MagicMock(errors=[], warnings=[], is_valid=True)
            r1 = runner.invoke(app, ["validate", str(f)])
            assert r1.exit_code != 0
            runner.invoke(app, ["validate", str(f), "--fix", "--yes"])
            r3 = runner.invoke(app, ["validate", str(f)])
        fixed = yaml.safe_load(f.read_text())
        assert fixed["info"].get("version") == "1.0.0"
        assert r3.exit_code == 0

class TestE2EMockTestgen:
    def test_testgen_valid_python(self, spec_yaml_file):
        out = spec_yaml_file.parent/"gen_tests"
        r = runner.invoke(app, ["testgen", str(spec_yaml_file), "--output", str(out), "--base-url","http://localhost:8080"])
        assert r.exit_code == 0 and out.exists()
        for f in out.glob("*.py"): ast.parse(f.read_text(encoding="utf-8"))

class TestE2EConvertPublishSearch:
    async def test_convert_then_publish(self, tmp_path, async_api_client: AsyncClient):
        imported = {"openapi":"3.1.0","info":{"title":"PetStore","version":"3.0.0"},
                    "paths":{"/pets":{"get":{"operationId":"listPets","responses":{"200":{"description":"OK"}}}}}}
        out = tmp_path/"petstore.yaml"
        with patch("apidoc.commands.convert._fetch_from_url", return_value=imported):
            r = runner.invoke(app, ["convert","--from-url","https://x.com/api.yaml","--output",str(out)])
        assert r.exit_code == 0 and out.exists()
        spec = yaml.safe_load(out.read_text())
        pub = await async_api_client.post("/specs", json={"name":"E2E PetStore","description":"","content":spec})
        assert pub.status_code == 201
        search = (await async_api_client.get("/specs/search?q=E2E PetStore")).json()
        assert search["total"] >= 1

class TestE2ETree:
    def test_tree_output(self, spec_yaml_file):
        r = runner.invoke(app, ["tree", str(spec_yaml_file)])
        assert r.exit_code == 0 and "/users" in r.output
    def test_tree_json(self, spec_yaml_file):
        r = runner.invoke(app, ["tree", str(spec_yaml_file), "--json"])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "paths" in data and "/users" in data["paths"]
