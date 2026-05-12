"""Extended publisher tests for coverage."""
from __future__ import annotations
import json
from unittest.mock import patch, MagicMock
import pytest, respx
from httpx import Response
from apidoc.api.publishers import publish_github, publish_gitlab, publish_redocly, publish_readme
from apidoc.utils.errors import AuthError, NetworkError

SPEC = {"openapi":"3.1.0","info":{"title":"T","version":"1"},"paths":{}}
CONTENT = "openapi: 3.1.0\ninfo:\n  title: T\n  version: '1'\npaths: {}\n"

class TestGitHubPublisher:
    @respx.mock
    def test_creates_new_file(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.github_token = "ghp_tok"; s.github_repo = "owner/repo"
            respx.get("https://api.github.com/repos/owner/repo/contents/openapi.yaml").mock(
                return_value=Response(404, json={}))
            respx.put("https://api.github.com/repos/owner/repo/contents/openapi.yaml").mock(
                return_value=Response(201, json={"content":{"html_url":"https://github.com/f"}}))
            r = publish_github(CONTENT)
        assert r["service"] == "github" and r["status"] == "published"

    @respx.mock
    def test_updates_existing_file(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.github_token = "ghp_tok"; s.github_repo = "owner/repo"
            respx.get("https://api.github.com/repos/owner/repo/contents/openapi.yaml").mock(
                return_value=Response(200, json={"sha":"abc123"}))
            respx.put("https://api.github.com/repos/owner/repo/contents/openapi.yaml").mock(
                return_value=Response(200, json={"content":{"html_url":"https://github.com/f"}}))
            r = publish_github(CONTENT)
        assert r["status"] == "published"

    def test_network_error(self):
        import httpx
        with patch("apidoc.api.publishers.settings") as s:
            s.github_token = "tok"; s.github_repo = "o/r"
            with patch("apidoc.api.publishers.httpx.get", side_effect=httpx.ConnectError("x")):
                with pytest.raises(NetworkError): publish_github(CONTENT)

class TestGitLabPublisher:
    @respx.mock
    def test_creates_file(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.gitlab_token = "glpat"; s.gitlab_project_id = "123"
            respx.put("https://gitlab.com/api/v4/projects/123/repository/files/openapi.yaml").mock(
                return_value=Response(200, json={}))
            r = publish_gitlab(CONTENT)
        assert r["service"] == "gitlab" and r["status"] == "published"

    @respx.mock
    def test_falls_back_to_post(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.gitlab_token = "glpat"; s.gitlab_project_id = "123"
            respx.put("https://gitlab.com/api/v4/projects/123/repository/files/openapi.yaml").mock(
                return_value=Response(400, json={"message":"not found"}))
            respx.post("https://gitlab.com/api/v4/projects/123/repository/files/openapi.yaml").mock(
                return_value=Response(201, json={}))
            r = publish_gitlab(CONTENT)
        assert r["status"] == "published"

class TestRedoclyPublisher:
    @respx.mock
    def test_success(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.redocly_token = "rdtok"
            respx.post("https://app.redocly.com/api/apis").mock(return_value=Response(200, json={}))
            r = publish_redocly(SPEC, "my-api")
        assert r["service"] == "redocly" and r["status"] == "published"

    def test_network_error(self):
        import httpx
        with patch("apidoc.api.publishers.settings") as s:
            s.redocly_token = "tok"
            with patch("apidoc.api.publishers.httpx.post", side_effect=httpx.ConnectError("x")):
                with pytest.raises(NetworkError): publish_redocly(SPEC, "api")

class TestReadMePublisher:
    @respx.mock
    def test_success(self):
        with patch("apidoc.api.publishers.settings") as s:
            s.readme_token = "rmtok"; s.readme_version = "stable"
            respx.post("https://api.readme.com/v2/branches/stable/apis").mock(
                return_value=Response(201, json={"upload": {"status": "pending"}}))
            r = publish_readme(CONTENT)
        assert r["service"] == "readme" and r["status"] == "published"

    def test_network_error(self):
        import httpx
        with patch("apidoc.api.publishers.settings") as s:
            s.readme_token = "tok"; s.readme_version = "stable"
            with patch("apidoc.api.publishers.httpx.post", side_effect=httpx.ConnectError("x")):
                with pytest.raises(NetworkError): publish_readme(CONTENT)
