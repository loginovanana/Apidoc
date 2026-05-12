"""Unit tests for publisher clients."""
from __future__ import annotations
from unittest.mock import patch
import pytest, respx
from httpx import Response
from apidoc.api.publishers import publish_swaggerhub, publish_github, publish_gitlab, publish_redocly, publish_readme
from apidoc.utils.errors import AuthError, NetworkError

SPEC = {"openapi":"3.1.0","info":{"title":"T","version":"1"},"paths":{}}
CONTENT = "openapi: 3.1.0\n"

class TestPublishers:
    def test_swaggerhub_no_token(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.swaggerhub_token = None; s.swaggerhub_owner = "x"
            with pytest.raises(AuthError): publish_swaggerhub(SPEC,"api","1.0")
    def test_swaggerhub_no_owner(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.swaggerhub_token = "tok"; s.swaggerhub_owner = None
            with pytest.raises(AuthError): publish_swaggerhub(SPEC,"api","1.0")
    @respx.mock
    def test_swaggerhub_success(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.swaggerhub_token="tok"; s.swaggerhub_owner="owner"
            respx.put("https://api.swaggerhub.com/apis/owner/api/1.0").mock(return_value=Response(200,json={}))
            r = publish_swaggerhub(SPEC,"api","1.0")
        assert r["service"]=="swaggerhub" and r["status"]=="published"
    @respx.mock
    def test_swaggerhub_401(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.swaggerhub_token="bad"; s.swaggerhub_owner="owner"
            respx.put("https://api.swaggerhub.com/apis/owner/api/1.0").mock(return_value=Response(401,json={}))
            with pytest.raises(AuthError): publish_swaggerhub(SPEC,"api","1.0")
    def test_github_no_token(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.github_token=None; s.github_repo="r/r"
            with pytest.raises(AuthError): publish_github(CONTENT)
    def test_gitlab_no_token(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.gitlab_token=None; s.gitlab_project_id="1"
            with pytest.raises(AuthError): publish_gitlab(CONTENT)
    def test_redocly_no_token(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.redocly_token=None
            with pytest.raises(AuthError): publish_redocly(SPEC,"api")
    def test_readme_no_token(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.readme_token=None; s.readme_version="v1"
            with pytest.raises(AuthError): publish_readme(CONTENT)
