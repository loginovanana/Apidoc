"""Unit tests for diff command."""
from __future__ import annotations
import json
from pathlib import Path
import pytest, yaml
from typer.testing import CliRunner
from apidoc.cli import app
from apidoc.commands.diff import _compare_specs

runner = CliRunner()

class TestCompareSpecs:
    def test_no_changes(self, sample_spec):
        r = _compare_specs(sample_spec, sample_spec)
        assert r["summary"]["total"] == 0
    def test_detects_removal(self, sample_spec, sample_spec_v2):
        r = _compare_specs(sample_spec, sample_spec_v2)
        assert any(c["type"]=="endpoint_removed" for c in r["breaking_changes"])
    def test_detects_addition(self, sample_spec, sample_spec_v2):
        r = _compare_specs(sample_spec, sample_spec_v2)
        assert any(c["type"]=="endpoint_added" for c in r["non_breaking_changes"])
    def test_summary_math(self, sample_spec, sample_spec_v2):
        r = _compare_specs(sample_spec, sample_spec_v2)
        s = r["summary"]; assert s["total"] == s["breaking"] + s["non_breaking"]

class TestDiffCommand:
    def test_same_files(self, spec_yaml_file):
        result = runner.invoke(app, ["diff", str(spec_yaml_file), str(spec_yaml_file)])
        assert result.exit_code == 0
    def test_breaking_exits_1(self, spec_yaml_file, tmp_path, sample_spec_v2):
        f2 = tmp_path/"v2.yaml"; f2.write_text(yaml.dump(sample_spec_v2))
        result = runner.invoke(app, ["diff", str(spec_yaml_file), str(f2)])
        assert result.exit_code != 0
    def test_json_flag(self, spec_yaml_file):
        result = runner.invoke(app, ["diff", str(spec_yaml_file), str(spec_yaml_file), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "summary" in data and "breaking_changes" in data
    def test_no_files_exits(self):
        result = runner.invoke(app, ["diff"])
        assert result.exit_code != 0
