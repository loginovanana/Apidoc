"""Unit tests for validate command."""
from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest, yaml
from typer.testing import CliRunner
from apidoc.cli import app
from apidoc.commands.validate import _run_local_validation

runner = CliRunner()

class TestValidateCommand:
    def test_valid_spec(self, spec_yaml_file):
        with patch("apidoc.api.validators.validate_external") as m:
            m.return_value = MagicMock(errors=[], warnings=[], is_valid=True)
            result = runner.invoke(app, ["validate", str(spec_yaml_file)])
        assert result.exit_code == 0
    def test_missing_file(self, tmp_path):
        result = runner.invoke(app, ["validate", str(tmp_path/"no.yaml")])
        assert result.exit_code != 0
    def test_json_flag(self, spec_yaml_file):
        with patch("apidoc.api.validators.validate_external") as m:
            m.return_value = MagicMock(errors=[], warnings=[], is_valid=True)
            result = runner.invoke(app, ["validate", str(spec_yaml_file), "--json"])
        assert result.exit_code == 0 and "valid" in json.loads(result.output)
    def test_no_external_skips_api(self, spec_yaml_file):
        with patch("apidoc.api.validators.validate_external") as m:
            runner.invoke(app, ["validate", str(spec_yaml_file), "--no-external"])
            m.assert_not_called()
    def test_network_error_warns(self, spec_yaml_file):
        from apidoc.utils.errors import NetworkError
        with patch("apidoc.api.validators.validate_external", side_effect=NetworkError("x")):
            result = runner.invoke(app, ["validate", str(spec_yaml_file)])
        assert result.exit_code == 0
    def test_fix_applies_missing_version(self, tmp_path):
        spec = {"openapi":"3.1.0","info":{"title":"T"},"paths":{}}
        f = tmp_path/"s.yaml"; f.write_text(yaml.dump(spec))
        with patch("apidoc.api.validators.validate_external") as m:
            m.return_value = MagicMock(errors=[], warnings=[], is_valid=True)
            runner.invoke(app, ["validate", str(f), "--fix", "--yes"])
        fixed = yaml.safe_load(f.read_text())
        assert fixed["info"].get("version") == "1.0.0"

class TestValidationEngine:
    def test_valid_spec(self, sample_spec):  assert _run_local_validation(sample_spec) == []
    def test_invalid_spec(self):             assert len(_run_local_validation({"openapi":"3.1.0","paths":{}})) > 0
    def test_returns_list(self, sample_spec): assert isinstance(_run_local_validation(sample_spec), list)
