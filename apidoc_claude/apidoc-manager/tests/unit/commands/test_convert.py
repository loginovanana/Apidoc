"""Unit tests for convert command."""
from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import patch
import pytest, yaml
from typer.testing import CliRunner
from apidoc.cli import app

runner = CliRunner()

class TestConvertCommand:
    def test_yaml_to_json(self, spec_yaml_file, tmp_path):
        out = tmp_path/"out.json"
        r = runner.invoke(app, ["convert", str(spec_yaml_file), "--to","json","--output",str(out)])
        assert r.exit_code == 0 and "openapi" in json.loads(out.read_text())
    def test_json_to_yaml(self, spec_json_file, tmp_path):
        out = tmp_path/"out.yaml"
        r = runner.invoke(app, ["convert", str(spec_json_file), "--to","yaml","--output",str(out)])
        assert r.exit_code == 0 and "openapi" in yaml.safe_load(out.read_text())
    def test_to_swagger2(self, spec_yaml_file, tmp_path):
        out = tmp_path/"sw.json"
        r = runner.invoke(app, ["convert", str(spec_yaml_file), "--to","swagger2","--output",str(out)])
        assert r.exit_code == 0 and json.loads(out.read_text())["swagger"] == "2.0"
    def test_json_output_flag(self, spec_yaml_file, tmp_path):
        out = tmp_path/"out.json"
        r = runner.invoke(app, ["convert", str(spec_yaml_file), "--to","json","--output",str(out),"--json"])
        assert r.exit_code == 0 and json.loads(r.output)["status"] == "ok"
    def test_no_target_exits(self):
        r = runner.invoke(app, ["convert"])
        assert r.exit_code != 0
    def test_from_url(self, tmp_path, sample_spec):
        out = tmp_path/"out.yaml"
        with patch("apidoc.commands.convert._fetch_from_url", return_value=sample_spec):
            r = runner.invoke(app, ["convert","--from-url","https://x.com/api.yaml","--output",str(out)])
        assert r.exit_code == 0 and out.exists()
