"""Tests for APIDoc CLI."""

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from apidoc_cli.main import app

runner = CliRunner()


class TestGenerateCommand:
    def test_generate_interactive(self, tmp_path):
        spec_file = tmp_path / "openapi.yaml"
        result = runner.invoke(app, ["generate", "--interactive", "--output", str(spec_file)], input="Test API\nTest Description\nhttp://localhost:8000\nn\n")
        assert result.exit_code == 0
        assert spec_file.exists()


class TestValidateCommand:
    def test_validate_valid_spec(self, tmp_path):
        valid_spec = {"openapi": "3.0.0", "info": {"title": "Test API", "version": "1.0.0"}, "paths": {"/test": {"get": {"responses": {"200": {"description": "OK"}}}}}}
        spec_file = tmp_path / "openapi.yaml"
        with open(spec_file, "w") as f:
            yaml.safe_dump(valid_spec, f)
        result = runner.invoke(app, ["validate", str(spec_file)])
        assert result.exit_code == 0

    def test_validate_invalid_spec(self, tmp_path):
        invalid_spec = {"openapi": "3.0.0", "info": {"title": "Test API"}, "paths": {}}
        spec_file = tmp_path / "invalid.yaml"
        with open(spec_file, "w") as f:
            yaml.safe_dump(invalid_spec, f)
        result = runner.invoke(app, ["validate", str(spec_file)])
        assert result.exit_code == 1

    def test_validate_with_json_output(self, tmp_path):
        valid_spec = {"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0.0"}, "paths": {}}
        spec_file = tmp_path / "spec.yaml"
        with open(spec_file, "w") as f:
            yaml.safe_dump(valid_spec, f)
        result = runner.invoke(app, ["validate", str(spec_file), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["valid"] is True


class TestDiffCommand:
    def test_diff_files(self, tmp_path):
        spec1 = {"openapi": "3.0.0", "info": {"title": "API v1", "version": "1.0.0"}, "paths": {"/users": {"get": {"responses": {"200": {"description": "OK"}}}}}}
        spec2 = {"openapi": "3.0.0", "info": {"title": "API v2", "version": "2.0.0"}, "paths": {"/users": {"get": {"responses": {"200": {"description": "OK"}}}, "post": {"responses": {"201": {"description": "Created"}}}}}}
        
        file1 = tmp_path / "spec1.yaml"
        file2 = tmp_path / "spec2.yaml"
        with open(file1, "w") as f: yaml.safe_dump(spec1, f)
        with open(file2, "w") as f: yaml.safe_dump(spec2, f)
        
        result = runner.invoke(app, ["diff", str(file1), str(file2)])
        assert result.exit_code == 0


class TestServerCommands:
    def test_server_status(self):
        result = runner.invoke(app, ["server", "status"])
        assert result.exit_code in [0, 1]
    
    def test_server_search(self):
        result = runner.invoke(app, ["server", "search", "test"])
        assert result.exit_code in [0, 1]
