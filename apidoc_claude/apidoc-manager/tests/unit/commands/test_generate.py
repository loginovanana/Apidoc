"""Unit tests for generate command."""
from __future__ import annotations
import json
from pathlib import Path
import pytest, yaml
from typer.testing import CliRunner
from apidoc.cli import app
from apidoc.plugins.generators.fastapi_gen import FastAPIGeneratorPlugin
from apidoc.plugins.generators.flask_gen import FlaskGeneratorPlugin
from apidoc.commands.validate import _run_local_validation

runner = CliRunner()

FASTAPI_SRC = """
from fastapi import FastAPI
api = FastAPI()
@api.get("/items")
def list_items(): return []
@api.post("/items")
def create_item(): return {}
@api.get("/items/{item_id}")
def get_item(item_id: int): return {}
@api.delete("/items/{item_id}")
def delete_item(item_id: int): return {}
"""

FLASK_SRC = """
from flask import Flask
app = Flask(__name__)
@app.route("/products", methods=["GET"])
def list_products(): return []
@app.route("/products", methods=["POST"])
def create_product(): return {}
"""

class TestFastAPIGenerator:
    def test_generates_paths(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        spec = FastAPIGeneratorPlugin().generate(str(src), {"title":"T","version":"1.0"})
        assert "/items" in spec["paths"] and "/items/{item_id}" in spec["paths"]
    def test_path_params_added(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        spec = FastAPIGeneratorPlugin().generate(str(src), {})
        params = spec["paths"]["/items/{item_id}"]["get"].get("parameters",[])
        assert any(p["name"]=="item_id" for p in params)
    def test_spec_passes_validation(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        spec = FastAPIGeneratorPlugin().generate(str(src), {"title":"T","version":"1.0"})
        assert _run_local_validation(spec) == []
    def test_from_directory(self, tmp_path):
        (tmp_path/"r.py").write_text(FASTAPI_SRC)
        spec = FastAPIGeneratorPlugin().generate(str(tmp_path), {"title":"T","version":"1.0"})
        assert len(spec["paths"]) > 0
    def test_unique_operation_ids(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        spec = FastAPIGeneratorPlugin().generate(str(src), {})
        ids = [op.get("operationId") for pi in spec["paths"].values()
               for op in pi.values() if isinstance(op,dict)]
        assert len(ids) == len(set(ids))

class TestFlaskGenerator:
    def test_generates_paths(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FLASK_SRC)
        spec = FlaskGeneratorPlugin().generate(str(src), {"title":"T","version":"1.0"})
        assert "/products" in spec["paths"]
    def test_no_angle_brackets(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FLASK_SRC)
        spec = FlaskGeneratorPlugin().generate(str(src), {})
        for k in spec["paths"]: assert "<" not in k

class TestGenerateCommand:
    def test_generate_fastapi(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        out = tmp_path/"spec.yaml"
        result = runner.invoke(app, ["generate", str(src), "--output", str(out), "--framework","fastapi"])
        assert result.exit_code == 0 and out.exists()
    def test_generate_json_flag(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        out = tmp_path/"spec.yaml"
        result = runner.invoke(app, ["generate", str(src), "--output", str(out), "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["status"] == "ok"
    def test_generate_json_format(self, tmp_path):
        src = tmp_path/"app.py"; src.write_text(FASTAPI_SRC)
        out = tmp_path/"spec.json"
        result = runner.invoke(app, ["generate", str(src), "--output", str(out), "--format","json"])
        assert result.exit_code == 0 and "openapi" in json.loads(out.read_text())
    def test_missing_source(self, tmp_path):
        result = runner.invoke(app, ["generate", str(tmp_path/"no.py")])
        assert result.exit_code != 0
    def test_no_args_exits(self):
        result = runner.invoke(app, ["generate"])
        assert result.exit_code != 0
