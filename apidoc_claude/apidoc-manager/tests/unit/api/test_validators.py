"""Unit tests for external validator client."""
from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest, respx
from httpx import Response
from apidoc.api.validators import ValidationResult, validate_external
from apidoc.utils.errors import NetworkError

class TestValidationResult:
    def test_valid_no_errors(self):
        r = ValidationResult([])
        assert r.is_valid is True and r.errors == [] and r.warnings == []
    def test_invalid_with_errors(self):
        r = ValidationResult([{"level": "ERROR", "message": "bad field"}])
        assert r.is_valid is False and len(r.errors) == 1
    def test_warnings_not_errors(self):
        r = ValidationResult([{"level": "WARNING", "message": "advisory"}])
        assert r.is_valid is True and len(r.warnings) == 1
    def test_to_dict(self):
        r = ValidationResult([{"level": "ERROR", "message": "e"}])
        d = r.to_dict()
        assert d["valid"] is False and "errors" in d and "summary" in d

class TestValidateExternal:
    @respx.mock
    def test_returns_valid_for_empty_messages(self):
        respx.post("https://validator.swagger.io/validator/debug").mock(
            return_value=Response(200, json={"messages": []}))
        result = validate_external({"openapi": "3.1.0", "info": {"title":"T","version":"1"}, "paths": {}})
        assert result.is_valid is True

    @respx.mock
    def test_returns_errors(self):
        respx.post("https://validator.swagger.io/validator/debug").mock(
            return_value=Response(200, json={"messages": [{"level":"ERROR","message":"bad"}]}))
        result = validate_external({})
        assert len(result.errors) == 1

    @respx.mock
    def test_handles_list_response(self):
        respx.post("https://validator.swagger.io/validator/debug").mock(
            return_value=Response(200, json=[]))
        result = validate_external({})
        assert result.is_valid is True

    def test_network_error_raises(self):
        import httpx
        with patch("apidoc.api.validators.httpx.post", side_effect=httpx.ConnectError("refused")):
            with pytest.raises(NetworkError): validate_external({})

    def test_other_exception_returns_empty(self):
        with patch("apidoc.api.validators.httpx.post", side_effect=ValueError("boom")):
            result = validate_external({})
        assert result.is_valid is True  # gracefully returns empty
