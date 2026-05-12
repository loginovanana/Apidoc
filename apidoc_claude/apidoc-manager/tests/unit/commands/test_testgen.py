"""Unit tests for testgen command."""
from __future__ import annotations
import ast
from pathlib import Path
import pytest
from typer.testing import CliRunner
from apidoc.cli import app
from apidoc.plugins.testgens.pytest_gen import PytestTestGenPlugin

runner = CliRunner()

class TestPytestPlugin:
    def test_generates_files(self, tmp_path, sample_spec):
        files = PytestTestGenPlugin().generate(sample_spec, str(tmp_path/"tests"), "http://localhost", {})
        assert len(files) >= 2
    def test_conftest_created(self, tmp_path, sample_spec):
        PytestTestGenPlugin().generate(sample_spec, str(tmp_path/"tests"), "http://x", {})
        assert (tmp_path/"tests"/"conftest.py").exists()
    def test_conftest_base_url(self, tmp_path, sample_spec):
        PytestTestGenPlugin().generate(sample_spec, str(tmp_path/"tests"), "http://myapi:9090", {})
        assert "http://myapi:9090" in (tmp_path/"tests"/"conftest.py").read_text()
    def test_valid_python_syntax(self, tmp_path, sample_spec):
        files = PytestTestGenPlugin().generate(sample_spec, str(tmp_path/"tests"), "http://x", {})
        for f in files: ast.parse(Path(f).read_text(encoding="utf-8"))
    def test_happy_path_in_output(self, tmp_path, sample_spec):
        PytestTestGenPlugin().generate(sample_spec, str(tmp_path/"tests"), "http://x", {})
        combined = "\n".join(f.read_text() for f in (tmp_path/"tests").glob("test_*.py"))
        assert "happy_path" in combined
    def test_output_dir_created(self, tmp_path, sample_spec):
        out = tmp_path/"new/tests"
        PytestTestGenPlugin().generate(sample_spec, str(out), "http://x", {})
        assert out.exists()

class TestTestgenCommand:
    def test_default_framework(self, spec_yaml_file, tmp_path):
        out = tmp_path/"gen"
        r = runner.invoke(app, ["testgen", str(spec_yaml_file), "--output", str(out)])
        assert r.exit_code == 0 and out.exists()
    def test_json_output(self, spec_yaml_file, tmp_path):
        import json
        out = tmp_path/"gen"
        r = runner.invoke(app, ["testgen", str(spec_yaml_file), "--output", str(out), "--json"])
        assert r.exit_code == 0
        data = json.loads(r.output, strict=False)
        assert data["status"] == "ok"
    def test_unknown_framework(self, spec_yaml_file, tmp_path):
        r = runner.invoke(app, ["testgen", str(spec_yaml_file), "--framework","nonexistent"])
        assert r.exit_code != 0
    def test_missing_spec(self, tmp_path):
        r = runner.invoke(app, ["testgen", str(tmp_path/"no.yaml")])
        assert r.exit_code != 0
