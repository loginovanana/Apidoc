"""Unit tests for command helper modules."""
from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import patch
import pytest, yaml
from apidoc.commands.diff import _collect_ops, _compare_specs, _render_diff, _req_body_fields
from apidoc.commands.mock import _build_response_body, _first_success_code, _generate_value
from apidoc.commands.tree import METHOD_COLORS, spec_to_tree_dict
from apidoc.commands.validate import FIX_SUGGESTIONS, _fix_missing_responses, _run_local_validation
from apidoc.commands.convert import _fetch_from_url, _openapi30_to_swagger2

class TestValidateHelpers:
    def test_fix_adds_responses(self):
        spec = {"paths":{"/x":{"get":{"operationId":"g"}}}}
        _fix_missing_responses(spec)
        assert "200" in spec["paths"]["/x"]["get"]["responses"]
    def test_fix_skips_existing(self):
        spec = {"paths":{"/x":{"get":{"responses":{"200":{"description":"OK"}}}}}}
        _fix_missing_responses(spec)
        assert list(spec["paths"]["/x"]["get"]["responses"].keys()) == ["200"]
    def test_fix_suggestions_not_empty(self): assert len(FIX_SUGGESTIONS) >= 2
    def test_fix_detects_missing_version(self):
        spec = {"openapi":"3.1.0","info":{"title":"T"},"paths":{}}
        assert any(s["check"](spec) for s in FIX_SUGGESTIONS)
    def test_run_local_valid(self, sample_spec):
        assert _run_local_validation(sample_spec) == []
    def test_run_local_invalid(self):
        assert len(_run_local_validation({"openapi":"3.1.0","paths":{}})) > 0
    def test_run_local_openapi30(self):
        spec = {"openapi":"3.0.3","info":{"title":"T","version":"1.0"},"paths":{}}
        assert isinstance(_run_local_validation(spec), list)

class TestDiffHelpers:
    def test_collect_ops(self, sample_spec):
        ops = _collect_ops(sample_spec)
        assert "GET /users" in ops and "POST /users" in ops
    def test_req_body_fields(self):
        op = {"requestBody":{"content":{"application/json":{
            "schema":{"type":"object","required":["name","email"]}}}}}
        assert _req_body_fields(op) == {"name","email"}
    def test_req_body_empty(self): assert _req_body_fields({}) == set()
    def test_compare_identical(self, sample_spec):
        r = _compare_specs(sample_spec, sample_spec)
        assert r["summary"]["total"] == 0
    def test_compare_removal(self, sample_spec, sample_spec_v2):
        r = _compare_specs(sample_spec, sample_spec_v2)
        assert any(c["type"]=="endpoint_removed" for c in r["breaking_changes"])
    def test_compare_addition(self, sample_spec, sample_spec_v2):
        r = _compare_specs(sample_spec, sample_spec_v2)
        assert any(c["type"]=="endpoint_added" for c in r["non_breaking_changes"])
    def test_compare_summary_math(self, sample_spec, sample_spec_v2):
        r = _compare_specs(sample_spec, sample_spec_v2)
        s = r["summary"]; assert s["total"] == s["breaking"] + s["non_breaking"]
    def test_compare_required_body_breaking(self):
        old = {"openapi":"3.1.0","info":{"title":"A","version":"1"},"paths":{
            "/x":{"post":{"responses":{"201":{"description":"OK"}},
                "requestBody":{"content":{"application/json":{"schema":{
                    "type":"object","required":["name"]}}}}}}}}
        new = {"openapi":"3.1.0","info":{"title":"A","version":"2"},"paths":{
            "/x":{"post":{"responses":{"201":{"description":"OK"}},
                "requestBody":{"content":{"application/json":{"schema":{
                    "type":"object","required":["name","email"]}}}}}}}}
        r = _compare_specs(old,new)
        assert any(c["type"]=="required_body_field_added" for c in r["breaking_changes"])
    def test_compare_summary_change_nonbreaking(self):
        old = {"openapi":"3.1.0","info":{"title":"A","version":"1"},"paths":{
            "/x":{"get":{"summary":"Old","responses":{"200":{"description":"OK"}}}}}}
        new = {"openapi":"3.1.0","info":{"title":"A","version":"2"},"paths":{
            "/x":{"get":{"summary":"New","responses":{"200":{"description":"OK"}}}}}}
        r = _compare_specs(old,new)
        assert r["summary"]["breaking"] == 0
        assert any(c["type"]=="summary_changed" for c in r["non_breaking_changes"])
    def test_render_no_crash(self, sample_spec, sample_spec_v2):
        _render_diff(_compare_specs(sample_spec, sample_spec_v2))
    def test_render_empty(self, sample_spec):
        _render_diff(_compare_specs(sample_spec, sample_spec))

class TestMockHelpers:
    def test_generate_string(self):  assert isinstance(_generate_value({"type":"string"}), str)
    def test_generate_integer(self): assert isinstance(_generate_value({"type":"integer"}), int)
    def test_generate_boolean(self): assert isinstance(_generate_value({"type":"boolean"}), bool)
    def test_generate_number(self):  assert isinstance(_generate_value({"type":"number"}), float)
    def test_generate_array(self):   assert isinstance(_generate_value({"type":"array","items":{"type":"string"}}), list)
    def test_generate_object(self):
        v = _generate_value({"type":"object","properties":{"a":{"type":"string"},"b":{"type":"integer"}}})
        assert isinstance(v, dict) and "a" in v and "b" in v
    def test_generate_enum(self):    assert _generate_value({"enum":["x","y"]}) == "x"
    def test_generate_example(self): assert _generate_value({"example":"hi"}) == "hi"
    def test_generate_default(self): assert _generate_value({"default":"ok"}) == "ok"
    def test_generate_email(self):   assert "@" in _generate_value({"type":"string","format":"email"})
    def test_generate_date(self):    assert len(_generate_value({"type":"string","format":"date"})) == 10
    def test_generate_uuid(self):    assert len(_generate_value({"type":"string","format":"uuid"})) == 36
    def test_generate_none(self):    assert _generate_value(None) is None
    def test_build_body_from_schema(self):
        op = {"responses":{"200":{"content":{"application/json":{
            "schema":{"type":"object","properties":{"id":{"type":"integer"}}}}}}}}
        assert isinstance(_build_response_body(op), dict)
    def test_build_body_fallback(self): assert _build_response_body({}) == {"message":"OK"}
    def test_first_success_200(self):   assert _first_success_code({"responses":{"200":{}}}) == 200
    def test_first_success_201(self):   assert _first_success_code({"responses":{"201":{}}}) == 201
    def test_first_success_default(self): assert _first_success_code({}) == 200
    def test_build_mock_app_routes(self, sample_spec):
        from apidoc.commands.mock import build_mock_app
        mock = build_mock_app(sample_spec, None, 0)
        paths = [r.path for r in mock.routes]
        assert any("/users" in p for p in paths)

class TestTreeHelpers:
    def test_structure(self, sample_spec):
        r = spec_to_tree_dict(sample_spec)
        assert r["api"]=="Test API" and r["version"]=="1.0.0"
        assert "/users" in r["paths"]
    def test_operations(self, sample_spec):
        r = spec_to_tree_dict(sample_spec)
        assert "GET" in r["paths"]["/users"] and "POST" in r["paths"]["/users"]
    def test_empty_paths(self):
        r = spec_to_tree_dict({"openapi":"3.1.0","info":{"title":"T","version":"1"},"paths":{}})
        assert r["paths"] == {}
    def test_method_colors(self):
        for m in ("GET","POST","PUT","PATCH","DELETE"): assert m in METHOD_COLORS

class TestConvertHelpers:
    def test_swagger2_structure(self, sample_spec):
        r = _openapi30_to_swagger2(sample_spec)
        assert r["swagger"]=="2.0" and "host" in r and "basePath" in r
    def test_swagger2_preserves_paths(self, sample_spec):
        r = _openapi30_to_swagger2(sample_spec)
        assert "/users" in r["paths"] and "/users/{id}" in r["paths"]
    def test_swagger2_definitions(self):
        spec = {"openapi":"3.0.3","info":{"title":"T","version":"1"},"paths":{},
                "components":{"schemas":{"User":{"type":"object"}}}}
        r = _openapi30_to_swagger2(spec)
        assert "definitions" in r and "User" in r["definitions"]
    def test_swagger2_requestbody_to_param(self):
        spec = {"openapi":"3.0.3","info":{"title":"T","version":"1"},"paths":{
            "/x":{"post":{"responses":{"201":{"description":"OK"}},
                "requestBody":{"required":True,"content":{"application/json":{
                    "schema":{"type":"object"}}}}}}}}
        r = _openapi30_to_swagger2(spec)
        params = r["paths"]["/x"]["post"]["parameters"]
        assert any(p.get("in")=="body" for p in params)
    def test_fetch_network_error(self):
        import httpx
        from apidoc.utils.errors import NetworkError
        with patch("apidoc.commands.convert.httpx.get", side_effect=httpx.ConnectError("x")):
            with pytest.raises(NetworkError): _fetch_from_url("https://x.invalid/api.yaml")
    def test_fetch_success_json(self, sample_spec):
        mock = type("R",(),{"headers":{"content-type":"application/json"},
            "text":json.dumps(sample_spec),"raise_for_status":lambda s:None})()
        with patch("apidoc.commands.convert.httpx.get", return_value=mock):
            r = _fetch_from_url("https://x.com/api.json")
        assert r["info"]["title"] == "Test API"
