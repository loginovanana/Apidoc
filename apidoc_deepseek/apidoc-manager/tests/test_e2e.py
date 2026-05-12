"""End-to-end tests for full workflows."""

from pathlib import Path
import yaml
import pytest
from deepdiff import DeepDiff


class TestGenerateValidateWorkflow:
    def test_generate_valid_spec(self, tmp_path: Path):
        spec_file = tmp_path / "openapi.yaml"
        spec = {"openapi": "3.0.3", "info": {"title": "Test", "version": "1.0.0"}, "paths": {"/test": {"get": {"responses": {"200": {"description": "OK"}}}}}}
        with open(spec_file, "w") as f:
            yaml.safe_dump(spec, f)
        assert spec_file.exists()
        with open(spec_file) as f:
            loaded = yaml.safe_load(f)
        assert loaded["info"]["title"] == "Test"


class TestDiffWorkflow:
    def test_diff_two_specs(self, tmp_path: Path):
        spec1 = {"openapi": "3.0.3", "info": {"title": "API v1", "version": "1.0.0"}, "paths": {"/users": {"get": {"responses": {"200": {"description": "OK"}}}}}}
        spec2 = {"openapi": "3.0.3", "info": {"title": "API v2", "version": "2.0.0"}, "paths": {"/users": {"get": {"responses": {"200": {"description": "OK"}}}, "post": {"responses": {"201": {"description": "Created"}}}}}}
        diff = DeepDiff(spec1, spec2, ignore_order=True)
        assert "dictionary_item_added" in diff or "values_changed" in diff
