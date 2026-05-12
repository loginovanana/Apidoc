"""Unit tests for utilities."""
from __future__ import annotations
import json
from pathlib import Path
import pytest, yaml
from apidoc.utils.errors import *
from apidoc.utils.spec import detect_format, load_spec, save_spec, spec_to_str

class TestErrorCodes:
    def test_network_error_code(self): assert NetworkError("t").code == "E001"
    def test_auth_error_code(self):    assert AuthError("t").code == "E002"
    def test_validation_error_code(self): assert ValidationError("t").code == "E003"
    def test_parse_error_code(self):   assert ParseError("t").code == "E004"
    def test_not_found_code(self):     assert NotFoundError("t").code == "E005"
    def test_server_error_code(self):  assert ServerError("t").code == "E006"
    def test_plugin_error_code(self):  assert PluginError("t").code == "E007"
    def test_config_error_code(self):  assert ConfigError("t").code == "E008"
    def test_error_detail(self):
        exc = NetworkError("msg","detail"); assert exc.message=="msg"; assert exc.detail=="detail"

class TestSpecUtils:
    def test_load_yaml(self, tmp_path, sample_spec):
        f = tmp_path/"spec.yaml"; f.write_text(yaml.dump(sample_spec))
        assert load_spec(f)["info"]["title"] == "Test API"
    def test_load_json(self, tmp_path, sample_spec):
        f = tmp_path/"spec.json"; f.write_text(json.dumps(sample_spec))
        assert load_spec(f)["info"]["version"] == "1.0.0"
    def test_load_missing_file(self):
        with pytest.raises(FileNotFoundError): load_spec("/nonexistent/path.yaml")
    def test_load_invalid_yaml(self, tmp_path):
        f = tmp_path/"bad.yaml"; f.write_text(": : invalid")
        with pytest.raises(Exception): load_spec(f)
    def test_save_yaml(self, tmp_path, sample_spec):
        f = tmp_path/"out.yaml"; save_spec(sample_spec, f)
        assert yaml.safe_load(f.read_text())["info"]["title"] == "Test API"
    def test_save_json(self, tmp_path, sample_spec):
        f = tmp_path/"out.json"; save_spec(sample_spec, f, "json")
        assert json.loads(f.read_text())["openapi"] == "3.1.0"
    def test_save_creates_dirs(self, tmp_path, sample_spec):
        f = tmp_path/"deep/nested/spec.yaml"; save_spec(sample_spec, f); assert f.exists()
    def test_spec_to_str_yaml(self, sample_spec):
        assert "openapi:" in spec_to_str(sample_spec)
    def test_spec_to_str_json(self, sample_spec):
        assert json.loads(spec_to_str(sample_spec,"json"))["info"]["title"] == "Test API"
    def test_detect_format_yaml(self): assert detect_format("spec.yaml") == "yaml"
    def test_detect_format_json(self): assert detect_format("spec.json") == "json"
