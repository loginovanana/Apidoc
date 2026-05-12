"""Tests for generate wizard and plugin loader."""
from __future__ import annotations
from unittest.mock import patch
import pytest
from apidoc.commands.generate import _interactive_wizard
from apidoc.plugins import load_plugins

class TestInteractiveWizard:
    def _run_wizard(self, prompts, confirms):
        with patch("apidoc.commands.generate.Prompt.ask", side_effect=prompts), \
             patch("apidoc.commands.generate.Confirm.ask", side_effect=confirms):
            return _interactive_wizard()

    def test_returns_valid_spec_structure(self):
        # title, version, desc, server_url, empty path → stop, bearer? no
        prompts = ["Wizard API", "1.0.0", "desc", "http://localhost:8000", ""]
        confirms = [False]  # no bearer
        spec = self._run_wizard(prompts, confirms)
        assert spec["openapi"] == "3.1.0"
        assert spec["info"]["title"] == "Wizard API"
        assert spec["info"]["version"] == "1.0.0"
        assert isinstance(spec["paths"], dict)

    def test_adds_bearer_when_confirmed(self):
        prompts = ["My API", "1.0.0", "", "http://x", ""]
        confirms = [True]  # bearer yes
        spec = self._run_wizard(prompts, confirms)
        assert "components" in spec
        assert "securitySchemes" in spec["components"]
        assert "security" in spec

    def test_server_url_in_servers(self):
        prompts = ["API", "1.0", "", "http://myserver:9000", ""]
        confirms = [False]
        spec = self._run_wizard(prompts, confirms)
        assert spec["servers"][0]["url"] == "http://myserver:9000"

class TestPluginLoader:
    def test_fastapi_plugin_importable(self):
        from apidoc.plugins.generators.fastapi_gen import FastAPIGeneratorPlugin
        assert callable(getattr(FastAPIGeneratorPlugin, "generate", None))

    def test_flask_plugin_importable(self):
        from apidoc.plugins.generators.flask_gen import FlaskGeneratorPlugin
        assert callable(getattr(FlaskGeneratorPlugin, "generate", None))

    def test_pytest_plugin_importable(self):
        from apidoc.plugins.testgens.pytest_gen import PytestTestGenPlugin
        assert callable(getattr(PytestTestGenPlugin, "generate", None))

    def test_invalid_group_returns_empty(self):
        result = load_plugins("apidoc.nonexistent.group")
        assert result == {}
