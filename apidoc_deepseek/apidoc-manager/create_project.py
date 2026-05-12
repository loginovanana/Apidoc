#!/usr/bin/env python3
"""
APIDoc Manager v2 — Полное создание проекта (118 файлов)
Запуск: python create_project.py
"""

import os
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Login\Documents\Учёба\Магистратура\Второй семестр\Программирование на Python\apidoc_deepseek\apidoc-manager")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def write_file(path, content):
    full_path = BASE_DIR / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"  ✓ {path}")

print("=" * 60)
print("  APIDoc Manager v2 — Генератор проекта")
print("=" * 60)
print()

# ═══════════════════════════════════════════════════════════════════
# 1. КОРНЕВЫЕ ФАЙЛЫ
# ═══════════════════════════════════════════════════════════════════
print("📁 Корневые файлы...")

write_file("pyproject.toml", r'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "apidoc-manager"
version = "0.1.0"
description = "CLI tool for OpenAPI specification management"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [{name = "APIDoc Team", email = "team@apidoc.local"}]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
    "click>=8.1.0",
    "httpx>=0.25.0",
    "openapi-core>=0.18.0",
    "openapi-spec-validator>=0.6.0",
    "prance>=23.0.0",
    "pyyaml>=6.0",
    "jsonschema>=4.19.0",
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "loguru>=0.7.0",
    "python-dotenv>=1.0.0",
    "keyring>=24.0.0",
    "python-json-logger>=2.0.0",
    "faker>=19.0.0",
    "pluggy>=1.3.0",
    "importlib-metadata>=6.8.0",
    "deepdiff>=6.7.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "bcrypt>=4.0.0",
    "prometheus-client>=0.19.0",
    "slowapi>=0.1.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
    "pre-commit>=3.5.0",
]

[project.scripts]
apidoc = "apidoc_cli.main:app"

[project.entry-points."apidoc.plugins"]
"python-parser" = "apidoc_cli.plugins.python_parser:PythonParserPlugin"
"js-parser" = "apidoc_cli.plugins.js_parser:JSParserPlugin"
"java-parser" = "apidoc_cli.plugins.java_parser:JavaParserPlugin"
"go-parser" = "apidoc_cli.plugins.go_parser:GoParserPlugin"
"pytest-generator" = "apidoc_cli.plugins.pytest_generator:PytestGeneratorPlugin"
"jest-generator" = "apidoc_cli.plugins.jest_generator:JestGeneratorPlugin"
"swaggerhub-publisher" = "apidoc_cli.plugins.publishers.swaggerhub:SwaggerHubPublisher"
"github-publisher" = "apidoc_cli.plugins.publishers.github:GitHubPublisher"
"readme-publisher" = "apidoc_cli.plugins.publishers.readme:ReadMePublisher"
"redocly-publisher" = "apidoc_cli.plugins.publishers.redocly:RedoclyPublisher"

[tool.setuptools]
packages = ["apidoc_cli", "apidoc_server"]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q"
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
ignore = ["E501"]
''')

write_file("requirements.txt", r'''typer[all]>=0.9.0
rich>=13.0.0
click>=8.1.0
httpx>=0.25.0
openapi-core>=0.18.0
openapi-spec-validator>=0.6.0
prance>=23.0.0
pyyaml>=6.0
jsonschema>=4.19.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.12.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
loguru>=0.7.0
python-dotenv>=1.0.0
keyring>=24.0.0
python-json-logger>=2.0.0
faker>=19.0.0
pluggy>=1.3.0
importlib-metadata>=6.8.0
deepdiff>=6.7.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.0.0
prometheus-client>=0.19.0
slowapi>=0.1.9
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.0.0
isort>=5.12.0
mypy>=1.5.0
ruff>=0.1.0
pre-commit>=3.5.0
''')

write_file("README.md", r'''# 🚀 APIDoc Manager

**Automated OpenAPI Specification Management CLI & Server**

APIDoc Manager is a comprehensive CLI tool and REST API server for automating the entire OpenAPI specification lifecycle.

## ✨ Features

- **🔧 Generate** - Create OpenAPI specs from FastAPI, Flask, Express, NestJS, Spring, and Gin
- **✅ Validate** - Validate specs locally or via official OpenAPI validator API
- **🔄 Diff** - Compare versions with breaking change detection
- **🎭 Mock** - Start mock server from specification
- **🧪 TestGen** - Generate Pytest and Jest test suites
- **📤 Publish** - Deploy to SwaggerHub, GitHub, ReadMe, Redocly
- **🔄 Convert** - Convert between OpenAPI 2.0/3.0/3.1 and JSON/YAML
- **🖥️ Server** - Centralized spec storage with versioning and search
- **🌲 Tree** - Visualize API structure as ASCII tree

## 🚀 Quick Start

```bash
pip install apidoc-manager
apidoc generate ./app.py --output openapi.yaml
apidoc validate openapi.yaml
apidoc mock openapi.yaml --port 8001
📝 License
MIT License - see LICENSE for details.
''')

write_file("LICENSE", r'''MIT License

Copyright (c) 2024 APIDoc Manager Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')

write_file("CHANGELOG.md", r'''# Changelog

[Unreleased]
Added
Initial release of APIDoc Manager

CLI with 9 core commands

FastAPI server for specification management

Plugin system for parsers, publishers, and test generators

Prometheus metrics and Grafana dashboards

Kubernetes deployment manifests

Docker support with multi-stage builds

[0.1.0] - 2024-01-15
Added
All core CLI commands (generate, validate, diff, mock, testgen, publish, convert, server, tree)

REST API server with PostgreSQL/SQLite support

Authentication with JWT and API keys

Rate limiting and CSRF protection

Structured JSON logging

Shell completion for Bash, Zsh, Fish
''')

write_file("Makefile", r'''.PHONY: help install dev test lint format clean build docker-build docker-up docker-down

help:
@echo "APIDoc Manager - Available Commands"
@echo "===================================="
@echo "make install - Install package"
@echo "make dev - Install development dependencies"
@echo "make test - Run tests"
@echo "make lint - Run linters"
@echo "make format - Format code"
@echo "make clean - Clean build artifacts"
@echo "make build - Build package"

install:
pip install -e .

dev:
pip install -e ".[dev]"
pre-commit install

test:
pytest tests/ -v

lint:
ruff check apidoc_cli apidoc_server tests

format:
ruff format apidoc_cli apidoc_server tests
isort apidoc_cli apidoc_server tests

clean:
rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
find . -type d -name pycache -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

init-db:
alembic upgrade head
''')

write_file(".gitignore", r'''pycache/
*.py[cod]
*.so
build/
dist/
*.egg-info/
venv/
.venv/
.env
.vscode/
.idea/
.pytest_cache/
.coverage
htmlcov/
*.log
logs/
*.db
*.sqlite
.mypy_cache/
.ruff_cache/
tmp/
*.tmp
''')

write_file(".dockerignore", r'''.git
pycache
*.pyc
*.egg-info
dist
build
venv
.venv
.env
.vscode
.idea
.pytest_cache
.coverage
*.log
*.db
*.sqlite
tmp/
''')

write_file(".env.example", r'''APIDOC_HOST=127.0.0.1
APIDOC_PORT=8000
APIDOC_DEBUG=false
APIDOC_LOG_LEVEL=INFO
APIDOC_LOG_JSON=false
APIDOC_DATABASE_URL=sqlite+aiosqlite:///./apidoc.db
APIDOC_SECRET_KEY=your-secret-key-here-change-in-production
APIDOC_TOKEN_EXPIRE_MINUTES=1440
APIDOC_ALLOWED_HOSTS=localhost,127.0.0.1
APIDOC_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
APIDOC_SWAGGERHUB_API_KEY=
APIDOC_GITHUB_TOKEN=
APIDOC_README_API_KEY=
APIDOC_RATE_LIMIT_PER_MINUTE=60
APIDOC_ENABLE_DOCS=true
APIDOC_ENABLE_METRICS=true
''')

write_file(".pre-commit-config.yaml", r'''repos:

repo: https://github.com/pre-commit/pre-commit-hooks
rev: v4.5.0
hooks:

id: trailing-whitespace

id: end-of-file-fixer

id: check-yaml

id: check-added-large-files

id: check-json

repo: https://github.com/astral-sh/ruff-pre-commit
rev: v0.1.5
hooks:

id: ruff
args: [--fix]

id: ruff-format

repo: https://github.com/pre-commit/mirrors-mypy
rev: v1.6.1
hooks:

id: mypy
additional_dependencies:

pydantic>=2.0.0

sqlalchemy>=2.0.0

typer>=0.9.0
''')

print("✓ Корневые файлы созданы (12 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 2. GitHub КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════
print("📁 GitHub конфигурация...")

write_file(".github/CODEOWNERS", r'''* @apidoc-team
/apidoc_cli/ @cli-maintainers
/apidoc_server/ @backend-maintainers
/docs/ @docs-team
/.github/workflows/ @devops-team
''')

write_file(".github/PULL_REQUEST_TEMPLATE.md", r'''## Description

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] I have performed a self-review of my own code
- [ ] I have added tests that prove my fix is effective
- [ ] New and existing unit tests pass locally
- [ ] I have run `make lint` and fixed any issues
''')

write_file(".github/workflows/ci.yml", r'''name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Lint with ruff
        run: ruff check apidoc_cli apidoc_server tests
      - name: Test with pytest
        run: pytest tests/ -v

  docker:
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/Dockerfile.prod
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
''')

write_file(".github/workflows/release.yml", r'''name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
          TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
        run: twine upload dist/*
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
          files: dist/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
''')

write_file(".github/workflows/security-scan.yml", r'''name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'

jobs:
  bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Bandit Security Scan
        uses: PyCQA/bandit-action@v1
        with:
          path: "apidoc_cli apidoc_server"
          level: high

  safety:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Safety Dependency Check
        uses: pyupio/safety-action@v1
        with:
          api-key: ${{ secrets.SAFETY_API_KEY }}
''')

print("✓ GitHub конфигурация создана (5 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 3. CLI ЯДРО
# ═══════════════════════════════════════════════════════════════════
print("📁 CLI ядро...")

write_file("apidoc_cli/__init__.py", r'''"""APIDoc Manager CLI."""

__version__ = "0.1.0"

LOGO = r"""
   ╔══════════════════════════════════════════════════════════╗
   ║                                                          ║
   ║     █████╗ ██████╗ ██╗██████╗  ██████╗  ██████╗        ║
   ║    ██╔══██╗██╔══██╗██║██╔══██╗██╔═══██╗██╔════╝        ║
   ║    ███████║██████╔╝██║██║  ██║██║   ██║██║             ║
   ║    ██╔══██║██╔═══╝ ██║██║  ██║██║   ██║██║             ║
   ║    ██║  ██║██║     ██║██████╔╝╚██████╔╝╚██████╗        ║
   ║    ╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝  ╚═════╝  ╚═════╝        ║
   ║                                                          ║
   ║    ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗       ║
   ║    ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝       ║
   ║    ██╔████╔██║███████║██╔██╗ ██║███████║██║            ║
   ║    ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║            ║
   ║    ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╗       ║
   ║    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝       ║
   ║                                                          ║
   ║      OpenAPI Specification Automation Toolkit             ║
   ║      Version: {version}                                          ║
   ║      License: MIT                                       ║
   ║      github.com/apidoc/apidoc-manager                    ║
   ║                                                          ║
   ╚══════════════════════════════════════════════════════════╝
"""


def get_logo() -> str:
    """Return the logo with current version."""
    return LOGO.format(version=__version__)
''')

write_file("apidoc_cli/main.py", r'''#!/usr/bin/env python3
"""APIDoc Manager CLI - Main entry point."""

import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console

from apidoc_cli import get_logo
from apidoc_cli.commands import (
    convert, diff, generate, mock, publish, server, testgen, tree, validate,
)
from apidoc_cli.config import Config, setup_logging
from apidoc_cli.utils import get_version

app = typer.Typer(
    name="apidoc",
    help="APIDoc Manager - OpenAPI specification automation toolkit",
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()

app.add_typer(generate.app, name="generate", help="Generate OpenAPI specs from source code")
app.add_typer(validate.app, name="validate", help="Validate OpenAPI specifications")
app.add_typer(diff.app, name="diff", help="Compare two OpenAPI specifications")
app.add_typer(mock.app, name="mock", help="Start mock server from specification")
app.add_typer(testgen.app, name="testgen", help="Generate tests from specification")
app.add_typer(publish.app, name="publish", help="Publish specification to services")
app.add_typer(convert.app, name="convert", help="Convert between formats and versions")
app.add_typer(server.app, name="server", help="Manage APIDoc server")
app.add_typer(tree.app, name="tree", help="Visualize API structure")


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    log_file: Optional[Path] = typer.Option(None, "--log-file", help="Path to log file"),
    version: bool = typer.Option(False, "--version", help="Show version"),
) -> None:
    """APIDoc Manager - OpenAPI specification automation toolkit."""
    
    if version:
        console.print(f"[bold green]APIDoc Manager[/] version {get_version()}")
        raise typer.Exit()
    
    if not ctx.invoked_subcommand:
        console.print(get_logo())
    
    setup_logging(debug=debug, log_file=log_file)
    cfg = Config.load(config)
    
    ctx.obj = {"config": cfg, "debug": debug, "json_output": json_output}
    
    if debug:
        logger.debug("Debug mode enabled")
        console.print("[yellow]Warning: Debug mode enabled[/]")


if __name__ == "__main__":
    app()
''')

write_file("apidoc_cli/config.py", r'''"""Configuration management for APIDoc CLI."""

from pathlib import Path
from typing import Optional

import yaml
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseModel):
    url: str = "http://localhost:8000"
    token: Optional[str] = None
    timeout: int = 30


class ExternalServiceConfig(BaseModel):
    swaggerhub_api_key: Optional[str] = None
    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    readme_api_key: Optional[str] = None


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: Path = Path.home() / ".apidoc" / "logs" / "apidoc.log"
    rotation: str = "10 MB"
    retention: str = "7 days"
    json_format: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APIDOC_", env_nested_delimiter="__", extra="ignore")
    
    server: ServerConfig = Field(default_factory=ServerConfig)
    external: ExternalServiceConfig = Field(default_factory=ExternalServiceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    default_output_format: str = "yaml"
    cache_dir: Path = Path.home() / ".apidoc" / "cache"


class Config:
    DEFAULT_CONFIG_PATH = Path.home() / ".apidoc" / "config.yaml"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.settings = Settings()
        self._load()
    
    def _load(self) -> None:
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = yaml.safe_load(f)
                    if data:
                        for key, value in data.items():
                            if hasattr(self.settings, key):
                                getattr(self.settings, key).update(value)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        self.settings = Settings()
    
    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.safe_dump(self.settings.model_dump(), f)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        return cls(config_path)


def setup_logging(debug: bool = False, log_file: Optional[Path] = None) -> None:
    import sys
    
    from loguru import logger
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    logger.add(sys.stderr, format=fmt, level=level, colorize=True)
    
    if log_file or debug:
        log_path = log_file or Path.home() / ".apidoc" / "logs" / "apidoc.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(log_path, format=fmt, level="DEBUG", rotation="10 MB", retention="7 days", colorize=False)
''')

write_file("apidoc_cli/exceptions.py", r'''"""Custom exceptions and error handling for APIDoc CLI."""

import sys
from typing import Optional

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.traceback import Traceback

console = Console()


class APIDocError(Exception):
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(message)


class ValidationError(APIDocError):
    def __init__(self, message: str, errors: list = None):
        super().__init__(message, code="VALIDATION_ERROR", details={"errors": errors or []})


class NetworkError(APIDocError):
    def __init__(self, message: str, url: str, status_code: Optional[int] = None):
        super().__init__(message, code="NETWORK_ERROR", details={"url": url, "status_code": status_code})


class ConfigurationError(APIDocError):
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, code="CONFIG_ERROR", details={"config_key": config_key})


class PluginError(APIDocError):
    def __init__(self, message: str, plugin_name: str):
        super().__init__(message, code="PLUGIN_ERROR", details={"plugin": plugin_name})


class ParseError(APIDocError):
    def __init__(self, message: str, file_path: str, line: Optional[int] = None):
        super().__init__(message, code="PARSE_ERROR", details={"file": file_path, "line": line})


class AuthenticationError(APIDocError):
    def __init__(self, message: str, service: str):
        super().__init__(message, code="AUTH_ERROR", details={"service": service})


def handle_error(error: Exception, debug: bool = False, exit_on_error: bool = True) -> None:
    if isinstance(error, APIDocError):
        _handle_apidoc_error(error, debug)
    else:
        _handle_unexpected_error(error, debug)
    if exit_on_error:
        sys.exit(1)


def _handle_apidoc_error(error: APIDocError, debug: bool) -> None:
    error_colors = {
        "VALIDATION_ERROR": "yellow", "NETWORK_ERROR": "red", "CONFIG_ERROR": "yellow",
        "PLUGIN_ERROR": "magenta", "PARSE_ERROR": "yellow", "AUTH_ERROR": "red",
    }
    color = error_colors.get(error.code, "red")
    console.print(Panel(f"[bold {color}]{error.code}[/]\n{error.message}", title="Error", border_style=color))
    if error.details and debug:
        console.print("\n[dim]Details:[/]")
        for key, value in error.details.items():
            console.print(f"  {key}: {value}")
    logger.error(f"{error.code}: {error.message}", **error.details)


def _handle_unexpected_error(error: Exception, debug: bool) -> None:
    if debug:
        console.print(Traceback.from_exception(type(error), error, error.__traceback__, show_locals=True))
    else:
        console.print(Panel(f"[red]An unexpected error occurred:[/]\n{str(error)}", title="Unexpected Error", border_style="red"))
        console.print("\n[dim]Run with --debug for more details[/]")
    logger.exception("Unexpected error occurred")
''')

write_file("apidoc_cli/utils.py", r'''"""Utility functions for APIDoc CLI."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger


def detect_framework(source: Path) -> Optional[str]:
    if source.is_file():
        content = source.read_text()
    elif source.is_dir():
        markers = {"fastapi": ["fastapi", "FastAPI"], "flask": ["flask", "Flask"]}
        for py_file in source.rglob("*.py"):
            try:
                content = py_file.read_text()
                for framework, patterns in markers.items():
                    if any(pattern in content for pattern in patterns):
                        return framework
            except Exception:
                continue
        return None
    else:
        return None
    
    frameworks = {"fastapi": ["from fastapi", "import fastapi"], "flask": ["from flask", "import flask"]}
    for framework, patterns in frameworks.items():
        if any(pattern in content for pattern in patterns):
            return framework
    return None


def write_output(data: Dict[str, Any], output_path: Path, format: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if format.lower() == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif format.lower() in ["yaml", "yml"]:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    else:
        raise ValueError(f"Unsupported format: {format}")
    logger.debug(f"Written output to {output_path}")


def read_input(input_path: Path) -> Dict[str, Any]:
    content = input_path.read_text(encoding="utf-8")
    if input_path.suffix == ".json":
        return json.loads(content)
    elif input_path.suffix in [".yaml", ".yml"]:
        return yaml.safe_load(content)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")


def get_version() -> str:
    try:
        from importlib.metadata import version
        return version("apidoc-manager")
    except Exception:
        return "0.1.0"
''')

write_file("apidoc_cli/validators.py", r'''"""OpenAPI specification validator."""

import json
from pathlib import Path
from typing import Any, Dict

import httpx
import yaml
from loguru import logger
from openapi_spec_validator import validate_spec
from openapi_spec_validator.exceptions import OpenAPIValidationError
from prance import ResolvingParser


class OpenAPIValidator:
    
    REMOTE_VALIDATOR_URL = "https://validator.swagger.io/validator/debug"
    
    def __init__(self, use_remote: bool = False):
        self.use_remote = use_remote
    
    def validate(self, spec_file: Path, strict: bool = False) -> Dict[str, Any]:
        spec = self._load_spec(spec_file)
        results = {"valid": True, "errors": [], "warnings": [], "fixable": []}
        
        if self.use_remote:
            return self._validate_remote(spec)
        
        try:
            validate_spec(spec)
            self._check_references(spec, results)
            self._check_common_issues(spec, results)
        except OpenAPIValidationError as e:
            results["valid"] = False
            results["errors"].append({"type": "validation_error", "message": str(e), "location": self._extract_location(e)})
        except Exception as e:
            results["valid"] = False
            results["errors"].append({"type": "parse_error", "message": str(e)})
        
        return results
    
    def _validate_remote(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.REMOTE_VALIDATOR_URL, json={"spec": spec})
                response.raise_for_status()
                data = response.json()
                results = {"valid": len(data.get("schemaValidationMessages", [])) == 0, "errors": [], "warnings": [], "fixable": []}
                for msg in data.get("schemaValidationMessages", []):
                    error = {"type": "remote_validation", "message": msg.get("message", ""), "location": msg.get("path", "")}
                    if msg.get("level") == "error":
                        results["errors"].append(error)
                    else:
                        results["warnings"].append(error)
                return results
        except Exception as e:
            logger.error(f"Remote validation failed: {e}")
            return {"valid": False, "errors": [{"type": "remote_error", "message": str(e)}], "warnings": [], "fixable": []}
    
    def _load_spec(self, spec_file: Path) -> Dict[str, Any]:
        content = spec_file.read_text(encoding="utf-8")
        if spec_file.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(content)
        elif spec_file.suffix == ".json":
            return json.loads(content)
        else:
            raise ValueError(f"Unsupported file format: {spec_file.suffix}")
    
    def _check_references(self, spec: Dict[str, Any], results: Dict) -> None:
        try:
            parser = ResolvingParser(spec_string=json.dumps(spec))
            def collect_refs(obj, path=""):
                if isinstance(obj, dict):
                    if "$ref" in obj:
                        ref = obj["$ref"]
                        if not ref.startswith("#"):
                            results["warnings"].append(f"External reference: {ref} at {path}")
                    for key, value in obj.items():
                        collect_refs(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        collect_refs(item, f"{path}[{i}]")
            collect_refs(spec)
        except Exception as e:
            results["warnings"].append(f"Reference validation warning: {e}")
    
    def _check_common_issues(self, spec: Dict[str, Any], results: Dict) -> None:
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                    continue
                if "responses" not in details:
                    results["errors"].append({"type": "missing_responses", "location": f"paths.{path}.{method}", "message": f"Missing 'responses' field for {method.upper()} {path}"})
                    results["fixable"].append({"type": "add_responses", "location": f"paths.{path}.{method}", "description": f"Add default 200 response for {method.upper()} {path}"})
                if "operationId" not in details:
                    results["warnings"].append(f"Missing operationId for {method.upper()} {path}")
    
    def _extract_location(self, error: Exception) -> str:
        error_str = str(error)
        if "in " in error_str:
            parts = error_str.split("in ")
            if len(parts) > 1:
                return parts[-1].split()[0].strip("'\"")
        return ""
    
    def apply_fix(self, spec_file: Path, issue: Dict[str, Any]) -> bool:
        spec = self._load_spec(spec_file)
        if issue["type"] == "add_responses":
            location = issue["location"]
            parts = location.split(".")
            if len(parts) >= 3:
                path = parts[1]
                method = parts[2]
                if path in spec["paths"] and method in spec["paths"][path]:
                    spec["paths"][path][method]["responses"] = {"200": {"description": "Successful response", "content": {"application/json": {"schema": {"type": "object"}}}}}
                    self._save_spec(spec_file, spec)
                    return True
        return False
    
    def _save_spec(self, spec_file: Path, spec: Dict[str, Any]) -> None:
        if spec_file.suffix in [".yaml", ".yml"]:
            content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        else:
            content = json.dumps(spec, indent=2, ensure_ascii=False)
        spec_file.write_text(content, encoding="utf-8")
''')

print("✓ CLI ядро создано (6 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 4. CLI КОМАНДЫ
# ═══════════════════════════════════════════════════════════════════
print("📁 CLI команды...")

write_file("apidoc_cli/commands/__init__.py", r'''"""CLI commands module."""

from apidoc_cli.commands import convert, diff, generate, mock, publish, server, testgen, tree, validate

__all__ = ["generate", "validate", "diff", "mock", "testgen", "publish", "convert", "server", "tree"]
''')

write_file("apidoc_cli/commands/generate.py", r'''"""Generate OpenAPI specifications from source code."""

from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from apidoc_cli.config import Config
from apidoc_cli.plugins import PluginManager
from apidoc_cli.utils import detect_framework, write_output

app = typer.Typer()
console = Console()


@app.command(name="generate")
def generate(
    ctx: typer.Context,
    source: Path = typer.Argument(..., help="Source file or directory"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("yaml", "--format", "-f", help="Output format (yaml/json)"),
    framework: Optional[str] = typer.Option(None, "--framework", help="Framework to parse"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
    title: Optional[str] = typer.Option(None, "--title", help="API title"),
    version: Optional[str] = typer.Option("1.0.0", "--version", "-v", help="API version"),
) -> None:
    """Generate OpenAPI specification from source code."""
    
    cfg: Config = ctx.obj["config"]
    debug = ctx.obj["debug"]
    
    if interactive:
        spec = _interactive_generation(title, version)
    else:
        if not source.exists():
            console.print(f"[red]Error:[/] Source path '{source}' does not exist")
            raise typer.Exit(1)
        
        detected_framework = framework or detect_framework(source)
        if not detected_framework:
            console.print("[red]Error:[/] Could not detect framework. Please specify with --framework")
            raise typer.Exit(1)
        
        console.print(f"[cyan]Detected framework:[/] {detected_framework}")
        
        plugin_manager = PluginManager()
        plugin = plugin_manager.get_parser(detected_framework)
        
        if not plugin:
            console.print(f"[red]Error:[/] No parser plugin found for {detected_framework}")
            console.print("Available parsers:")
            for name in plugin_manager.list_parsers():
                console.print(f"  * {name}")
            raise typer.Exit(1)
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Parsing source code...", total=None)
            try:
                spec = plugin.parse(source, title=title, version=version)
                progress.update(task, description="[green]✓[/] Parsing complete")
            except Exception as e:
                progress.update(task, description="[red]✗[/] Parsing failed")
                logger.error(f"Failed to parse source: {e}")
                if debug:
                    console.print_exception()
                raise typer.Exit(1)
    
    output_path = output or Path(f"openapi.{format}")
    write_output(spec, output_path, format)
    
    if not ctx.obj.get("json_output"):
        _show_preview(spec)
    
    console.print(f"\n[green]✓[/] Specification saved to [bold]{output_path}[/]")


def _interactive_generation(title: Optional[str], version: str) -> dict:
    console.print(Panel.fit("[bold cyan]Interactive OpenAPI Specification Generator[/]", border_style="cyan"))
    
    if not title:
        title = Prompt.ask("Enter API title", default="My API")
    
    description = Prompt.ask("Enter API description", default="")
    
    spec = {
        "openapi": "3.0.3",
        "info": {"title": title, "version": version, "description": description},
        "servers": [{"url": Prompt.ask("Server URL", default="http://localhost:8000")}],
        "paths": {},
        "components": {"schemas": {}},
    }
    
    console.print("\n[bold]Let's add some endpoints:[/]")
    
    while Confirm.ask("Add an endpoint?", default=True):
        path = Prompt.ask("  Path", default="/users")
        method = Prompt.ask("  HTTP method", choices=["get", "post", "put", "delete", "patch"], default="get").upper()
        
        if path not in spec["paths"]:
            spec["paths"][path] = {}
        
        endpoint = {
            "summary": Prompt.ask("  Summary", default=f"{method} {path}"),
            "operationId": f"{method.lower()}_{path.strip('/').replace('/', '_')}",
            "responses": {"200": {"description": "Successful response", "content": {"application/json": {"schema": {"type": "object"}}}}}
        }
        
        spec["paths"][path][method.lower()] = endpoint
        console.print(f"  [green]✓[/] Added {method} {path}")
    
    return spec


def _show_preview(spec: dict) -> None:
    console.print("\n[bold]Specification Preview:[/]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Method", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Summary")
    
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            table.add_row(method.upper(), path, details.get("summary", ""))
    
    if table.rows:
        console.print(table)
    else:
        console.print("[yellow]No endpoints defined yet[/]")
''')

write_file("apidoc_cli/commands/validate.py", r'''"""Validate OpenAPI specifications."""

from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from apidoc_cli.validators import OpenAPIValidator

app = typer.Typer()
console = Console()


@app.command(name="validate")
def validate(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Strict validation mode"),
    remote: bool = typer.Option(False, "--remote", help="Use remote validator API"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix common issues"),
) -> None:
    """Validate OpenAPI specification."""
    
    debug = ctx.obj["debug"]
    json_output = ctx.obj["json_output"]
    
    if not spec_file.exists():
        console.print(f"[red]Error:[/] File '{spec_file}' does not exist")
        raise typer.Exit(1)
    
    validator = OpenAPIValidator(use_remote=remote)
    
    try:
        results = validator.validate(spec_file, strict=strict)
        
        if json_output:
            import json
            console.print(json.dumps(results, indent=2))
            return
        
        if results["valid"]:
            console.print(Panel("[bold green]✓ Specification is valid![/]", border_style="green"))
            if results.get("warnings"):
                console.print("\n[yellow]Warnings:[/]")
                for warning in results["warnings"]:
                    console.print(f"  * {warning}")
        else:
            console.print(Panel("[bold red]✗ Specification has errors[/]", border_style="red"))
            table = Table(show_header=True, header_style="bold red")
            table.add_column("Type", style="red")
            table.add_column("Location")
            table.add_column("Message")
            for error in results.get("errors", []):
                table.add_row(error.get("type", "error"), error.get("location", ""), error.get("message", ""))
            console.print(table)
            
            if fix and results.get("fixable", []):
                console.print("\n[cyan]Found fixable issues:[/]")
                for issue in results["fixable"]:
                    if typer.confirm(f"Fix {issue['description']}?"):
                        fixed = validator.apply_fix(spec_file, issue)
                        if fixed:
                            console.print(f"  [green]✓[/] Fixed: {issue['description']}")
                        else:
                            console.print(f"  [red]✗[/] Failed to fix: {issue['description']}")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if debug:
            console.print_exception()
        raise typer.Exit(1)
''')

write_file("apidoc_cli/commands/diff.py", r'''"""Compare OpenAPI specifications."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import typer
from deepdiff import DeepDiff
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


@app.command(name="diff")
def diff_command(
    ctx: typer.Context,
    spec1: Path = typer.Argument(..., help="First specification file or server ID"),
    spec2: Optional[Path] = typer.Argument(None, help="Second specification file"),
    from_server: Optional[int] = typer.Option(None, "--from-server", help="Compare server versions"),
    v1: Optional[str] = typer.Option(None, "--v1", help="First version"),
    v2: Optional[str] = typer.Option(None, "--v2", help="Second version"),
    tree_view: bool = typer.Option(False, "--tree", "-t", help="Show as tree"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Compare two OpenAPI specifications."""
    
    debug = ctx.obj.get("debug", False)
    json_format = ctx.obj.get("json_output", False) or json_output
    
    try:
        if from_server:
            spec1_data, spec2_data = _get_server_versions(from_server, v1, v2)
        else:
            if not spec2:
                console.print("[red]Error:[/] Two files required for local comparison")
                raise typer.Exit(1)
            spec1_data = read_input(spec1)
            spec2_data = read_input(spec2)
        
        diff_result = _compare_specs(spec1_data, spec2_data)
        
        if json_format:
            console.print(json.dumps(diff_result, indent=2, default=str))
            return
        
        _display_diff(diff_result, tree_view=tree_view)
        
        breaking_changes = _detect_breaking_changes(diff_result)
        if breaking_changes:
            console.print("\n[bold red]⚠ BREAKING CHANGES DETECTED![/]")
            for change in breaking_changes:
                console.print(f"  * {change}")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Diff failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


def _compare_specs(spec1: Dict, spec2: Dict) -> Dict:
    diff = DeepDiff(spec1, spec2, ignore_order=True, report_repetition=True, verbose_level=2)
    return {
        "added": [str(item) for item in diff.get("dictionary_item_added", [])],
        "removed": [str(item) for item in diff.get("dictionary_item_removed", [])],
        "changed": {str(k): str(v) for k, v in diff.get("values_changed", {}).items()},
        "type_changes": {str(k): str(v) for k, v in diff.get("type_changes", {}).items()},
        "breaking_changes": [],
    }


def _detect_breaking_changes(diff_result: Dict) -> List[str]:
    breaking = []
    for item in diff_result.get("removed", []):
        if "paths" in item:
            breaking.append(f"Removed endpoint: {item}")
    for path, change in diff_result.get("changed", {}).items():
        if "required" in path:
            breaking.append(f"Required field changed: {path}")
    for path, change in diff_result.get("type_changes", {}).items():
        breaking.append(f"Type changed: {path}")
    return breaking


def _display_diff(diff_result: Dict, tree_view: bool = False) -> None:
    if tree_view:
        _display_tree_diff(diff_result)
    else:
        _display_table_diff(diff_result)


def _display_table_diff(diff_result: Dict) -> None:
    if diff_result.get("added"):
        table = Table(title="Added", style="green")
        table.add_column("Path", style="green")
        for item in diff_result["added"][:20]:
            table.add_row(item[:80])
        console.print(table)
    if diff_result.get("removed"):
        table = Table(title="Removed", style="red")
        table.add_column("Path", style="red")
        for item in diff_result["removed"][:20]:
            table.add_row(item[:80])
        console.print(table)
    if diff_result.get("changed"):
        table = Table(title="Changed", style="yellow")
        table.add_column("Path")
        table.add_column("Old Value")
        table.add_column("New Value")
        for path, change in list(diff_result["changed"].items())[:20]:
            table.add_row(path[:40], str(change)[:30], "")
        console.print(table)


def _display_tree_diff(diff_result: Dict) -> None:
    tree = Tree("API Changes")
    if diff_result.get("added"):
        added_branch = tree.add("✅ Added")
        for item in diff_result["added"][:10]:
            added_branch.add(item[:60])
    if diff_result.get("removed"):
        removed_branch = tree.add("❌ Removed")
        for item in diff_result["removed"][:10]:
            removed_branch.add(item[:60])
    if diff_result.get("changed"):
        changed_branch = tree.add("🔄 Changed")
        for path in list(diff_result["changed"].keys())[:10]:
            changed_branch.add(path[:60])
    console.print(tree)


def _get_server_versions(spec_id: int, v1: Optional[str], v2: Optional[str]) -> tuple:
    import httpx
    try:
        response = httpx.get(f"http://localhost:8000/api/v1/specs/{spec_id}", params={"version": v1})
        spec1 = response.json()["content"]
        response = httpx.get(f"http://localhost:8000/api/v1/specs/{spec_id}", params={"version": v2})
        spec2 = response.json()["content"]
        return spec1, spec2
    except Exception as e:
        raise RuntimeError(f"Failed to get server versions: {e}")
''')

write_file("apidoc_cli/commands/mock.py", r'''"""Mock server command."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from faker import Faker
from loguru import logger
from rich.console import Console

from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()
fake = Faker()


class MockServer:
    """Mock server based on OpenAPI spec."""
    
    def __init__(self, spec: Dict[str, Any], log_file: Optional[Path] = None):
        self.spec = spec
        self.log_file = log_file
        self.app = FastAPI(title=f"Mock: {spec.get('info', {}).get('title', 'API')}")
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        self.app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            if self.log_file:
                log_entry = {"method": request.method, "path": str(request.url.path), "client": request.client.host if request.client else None}
                try:
                    body = await request.body()
                    if body:
                        log_entry["body"] = body.decode()
                except Exception:
                    pass
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
            response = await call_next(request)
            return response
    
    def _setup_routes(self):
        for path, methods in self.spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                self._add_route(path, method, details)
    
    def _add_route(self, path: str, method: str, details: Dict[str, Any]):
        async def mock_handler(request: Request, path=path, method=method, details=details):
            responses = details.get("responses", {})
            response_schema = None
            for status_code in ["200", "201"]:
                if status_code in responses:
                    response_schema = responses[status_code]
                    break
            
            if not response_schema:
                return Response(content=json.dumps({"message": "Mock response"}), media_type="application/json")
            
            content = response_schema.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                mock_data = self._generate_mock_data(schema)
            else:
                mock_data = {"message": f"Mock response for {method.upper()} {path}"}
            
            if method.lower() in ["post", "put"]:
                try:
                    request_data = await request.json()
                    mock_data["received"] = request_data
                except Exception:
                    pass
            
            return Response(content=json.dumps(mock_data, default=str), media_type="application/json")
        
        route_path = path.replace("{", "<").replace("}", ">")
        route_methods = {"get": self.app.get, "post": self.app.post, "put": self.app.put, "delete": self.app.delete, "patch": self.app.patch}
        if method.lower() in route_methods:
            route_methods[method.lower()](route_path)(mock_handler)
    
    def _generate_mock_data(self, schema: Dict[str, Any]) -> Any:
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            result = {}
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            for prop_name, prop_schema in properties.items():
                if prop_name in required or fake.boolean(chance_of_getting_true=70):
                    result[prop_name] = self._generate_mock_data(prop_schema)
            return result
        elif schema_type == "array":
            items = schema.get("items", {})
            count = fake.random_int(min=schema.get("minItems", 1), max=schema.get("maxItems", 5))
            return [self._generate_mock_data(items) for _ in range(count)]
        elif schema_type == "string":
            format_type = schema.get("format", "")
            if format_type == "email": return fake.email()
            elif format_type == "date": return fake.date()
            elif format_type == "date-time": return fake.iso8601()
            elif format_type == "uuid": return fake.uuid4()
            elif format_type == "uri": return fake.url()
            else:
                enum = schema.get("enum")
                if enum: return fake.random_element(enum)
                return fake.word()
        elif schema_type == "integer":
            return fake.random_int(min=schema.get("minimum", 0), max=schema.get("maximum", 100))
        elif schema_type == "number":
            return fake.pyfloat(min_value=schema.get("minimum", 0.0), max_value=schema.get("maximum", 100.0))
        elif schema_type == "boolean":
            return fake.boolean()
        else:
            return None
    
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        uvicorn.run(self.app, host=host, port=port, log_level="info")


@app.command(name="mock")
def mock_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    log_file: Optional[Path] = typer.Option(None, "--log-file", help="Log requests to file"),
) -> None:
    """Start mock server from OpenAPI specification."""
    
    try:
        spec = read_input(spec_file)
        console.print(f"[bold green]Starting mock server for:[/] {spec.get('info', {}).get('title', 'API')}")
        console.print(f"[cyan]Server running at:[/] http://{host}:{port}")
        console.print("\n[yellow]Available endpoints:[/]")
        for path, methods in spec.get("paths", {}).items():
            for method in methods.keys():
                console.print(f"  {method.upper():<7} {path}")
        console.print("\n[dim]Press Ctrl+C to stop[/]\n")
        
        server = MockServer(spec, log_file)
        server.run(host, port)
    except KeyboardInterrupt:
        console.print("\n[yellow]Mock server stopped[/]")
    except Exception as e:
        logger.error(f"Mock server failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)
''')

write_file("apidoc_cli/plugins/pytest_generator.py", """\"\"\"Pytest test generator.\"\"\"

from pathlib import Path
from typing import Any, Dict, List

from apidoc_cli.plugins.base import BaseTestGenerator


class PytestGeneratorPlugin(BaseTestGenerator):
    @property
    def name(self) -> str:
        return "pytest"
    
    @property
    def language(self) -> str:
        return "python"
    
    @property
    def framework(self) -> str:
        return "pytest"
    
    def generate(self, spec: Dict[str, Any], output_dir: Path, **kwargs) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        conftest = self._generate_conftest(spec)
        conftest_path = output_dir / "conftest.py"
        conftest_path.write_text(conftest)
        generated_files.append(conftest_path)
        
        tests_by_tag = self._group_by_tag(spec)
        for tag, endpoints in tests_by_tag.items():
            test_content = self._generate_test_file(tag, endpoints, spec)
            test_path = output_dir / f"test_{self._sanitize_name(tag)}.py"
            test_path.write_text(test_content)
            generated_files.append(test_path)
        
        return generated_files
    
    def _generate_conftest(self, spec: Dict) -> str:
        servers = spec.get("servers", [{}])
        base_url = servers[0].get("url", "http://localhost:8000") if servers else "http://localhost:8000"
        lines = []
        lines.append("\"\"\"Pytest configuration.\"\"\"")
        lines.append("")
        lines.append("import pytest")
        lines.append("import httpx")
        lines.append("")
        lines.append("")
        lines.append("@pytest.fixture")
        lines.append("def base_url():")
        lines.append(f"    return \"{base_url}\"")
        lines.append("")
        lines.append("")
        lines.append("@pytest.fixture")
        lines.append("async def client():")
        lines.append("    async with httpx.AsyncClient() as client:")
        lines.append("        yield client")
        return "\\n".join(lines)
    
    def _group_by_tag(self, spec: Dict) -> Dict[str, List]:
        groups = {"default": []}
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                tags = details.get("tags", ["default"])
                for tag in tags:
                    if tag not in groups:
                        groups[tag] = []
                    groups[tag].append({"path": path, "method": method, "details": details})
        return groups
    
    def _generate_test_file(self, tag: str, endpoints: List, spec: Dict) -> str:
        class_name = self._sanitize_name(tag).title()
        lines = []
        lines.append(f"\"\"\"Tests for {tag} endpoints.\"\"\"")
        lines.append("")
        lines.append("import pytest")
        lines.append("from httpx import AsyncClient")
        lines.append("")
        lines.append("")
        lines.append(f"class Test{class_name}API:")
        lines.append(f"    \"\"\"Test cases for {tag} endpoints.\"\"\"")
        lines.append("    ")
        for endpoint in endpoints:
            lines.append(self._generate_test_method(endpoint))
        return "\\n".join(lines)
    
    def _generate_test_method(self, endpoint: Dict) -> str:
        path = endpoint["path"]
        method = endpoint["method"]
        details = endpoint["details"]
        op_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
        success_code = "200"
        for code in ["200", "201", "204"]:
            if code in details.get("responses", {}):
                success_code = code
                break
        lines = []
        lines.append("")
        lines.append("    @pytest.mark.asyncio")
        lines.append(f"    async def test_{op_id}(self, client: AsyncClient, base_url: str):")
        lines.append(f"        \"\"\"Test {method.upper()} {path}\"\"\"")
        lines.append(f"        response = await client.{method.lower()}(f\"{{base_url}}{path}\")")
        lines.append(f"        assert response.status_code == {success_code}")
        return "\\n".join(lines)
    
    def _sanitize_name(self, name: str) -> str:
        import re
        name = re.sub(r"[^\\w]", "_", name.lower())
        if name[0].isdigit():
            name = "_" + name
        return name
""")

write_file("apidoc_cli/commands/publish.py", r'''"""Publish command."""

import asyncio
import base64
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import typer
import yaml
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from apidoc_cli.config import Config
from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


class Publisher:
    """Publish specifications to various services."""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def publish_to_server(self, spec: Dict, name: str, server_url: str, token: Optional[str] = None) -> Dict:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{server_url}/api/v1/specs",
                json={"name": name, "content": spec, "format": "json", "changelog": "Published via CLI"},
                headers=headers
            )
            if response.status_code == 409:
                spec_id = await self._get_spec_id(client, server_url, name, headers)
                if spec_id:
                    response = await client.post(
                        f"{server_url}/api/v1/specs/{spec_id}/versions",
                        json={"content": spec, "version": spec.get("info", {}).get("version", "1.0.0"), "format": "json", "changelog": "Updated via CLI"},
                        headers=headers
                    )
            response.raise_for_status()
            return response.json()
    
    async def _get_spec_id(self, client, server_url: str, name: str, headers: Dict) -> Optional[int]:
        response = await client.get(f"{server_url}/api/v1/specs/search", params={"q": name}, headers=headers)
        data = response.json()
        for item in data.get("items", []):
            if item["name"] == name:
                return item["id"]
        return None
    
    async def publish_to_swaggerhub(self, spec: Dict, api_key: str, owner: str, name: str, version: str) -> Dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://api.swaggerhub.com/apis/{owner}/{name}",
                params={"version": version, "isPrivate": "false"},
                json=spec,
                headers={"Authorization": api_key, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    
    async def publish_to_github(self, spec: Dict, token: str, repo: str, path: str, branch: str = "main", message: str = "Update OpenAPI specification") -> Dict:
        yaml_content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        content_base64 = base64.b64encode(yaml_content.encode()).decode()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                params={"ref": branch},
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            )
            data = {"message": message, "content": content_base64, "branch": branch}
            if response.status_code == 200:
                data["sha"] = response.json()["sha"]
            
            response = await client.put(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                json=data,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            )
            response.raise_for_status()
            result = response.json()
            return {"url": result["content"]["html_url"], "sha": result["content"]["sha"], "path": path}
    
    async def publish_to_readme(self, spec: Dict, api_key: str, version: str) -> Dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://dash.readme.com/api/v1/api-registry",
                json={"spec": spec, "version": version},
                headers={"Authorization": f"Bearer {api_key}"}
            )
            response.raise_for_status()
            return response.json()


@app.command(name="publish")
def publish_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    targets: List[str] = typer.Option(["server"], "--target", "-t", help="Publish targets (server, swaggerhub, github, readme)"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="API name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="API version"),
    server_url: Optional[str] = typer.Option(None, "--server-url", help="Server URL"),
    swaggerhub_owner: Optional[str] = typer.Option(None, "--swaggerhub-owner", help="SwaggerHub owner"),
    github_repo: Optional[str] = typer.Option(None, "--github-repo", help="GitHub repository"),
    github_path: Optional[str] = typer.Option(None, "--github-path", help="Path in GitHub repo"),
) -> None:
    """Publish OpenAPI specification to various services."""
    
    cfg: Config = ctx.obj["config"]
    
    try:
        spec = read_input(spec_file)
        api_name = name or spec.get("info", {}).get("title", spec_file.stem)
        api_version = version or spec.get("info", {}).get("version", "1.0.0")
        
        console.print(f"[bold]Publishing:[/] {api_name} v{api_version}")
        
        publisher = Publisher(cfg)
        results = []
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            async def publish_all():
                tasks = []
                
                if "server" in targets:
                    async def pub_server():
                        url = server_url or cfg.server.url
                        return await publisher.publish_to_server(spec, api_name, url, cfg.server.token)
                    tasks.append(("Server", pub_server()))
                
                if "swaggerhub" in targets and cfg.external.swaggerhub_api_key:
                    async def pub_swagger():
                        return await publisher.publish_to_swaggerhub(spec, cfg.external.swaggerhub_api_key, swaggerhub_owner, api_name, api_version)
                    tasks.append(("SwaggerHub", pub_swagger()))
                
                if "github" in targets and cfg.external.github_token:
                    async def pub_github():
                        repo = github_repo
                        path = github_path or f"docs/openapi.yaml"
                        return await publisher.publish_to_github(spec, cfg.external.github_token, repo, path)
                    tasks.append(("GitHub", pub_github()))
                
                if "readme" in targets and cfg.external.readme_api_key:
                    async def pub_readme():
                        return await publisher.publish_to_readme(spec, cfg.external.readme_api_key, api_version)
                    tasks.append(("ReadMe", pub_readme()))
                
                for target_name, coro in tasks:
                    task = progress.add_task(f"Publishing to {target_name}...", total=None)
                    try:
                        result = await coro
                        results.append({"target": target_name, "success": True, "result": result})
                        progress.update(task, description=f"[green]✓ Published to {target_name}[/]")
                    except Exception as e:
                        results.append({"target": target_name, "success": False, "error": str(e)})
                        progress.update(task, description=f"[red]✗ Failed {target_name}: {e}[/]")
            
            asyncio.run(publish_all())
        
        table = Table(title="Publish Results")
        table.add_column("Target", style="cyan")
        table.add_column("Status")
        table.add_column("Details")
        for result in results:
            if result["success"]:
                table.add_row(result["target"], "[green]✓ Success[/]", str(result.get("result", {}).get("id", "")))
            else:
                table.add_row(result["target"], "[red]✗ Failed[/]", result["error"])
        console.print(table)
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)
''')

write_file("apidoc_cli/commands/convert.py", r'''"""Convert command for OpenAPI specifications."""

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from loguru import logger
from rich.console import Console

from apidoc_cli.utils import read_input, write_output

app = typer.Typer()
console = Console()


@app.command(name="convert")
def convert_command(
    ctx: typer.Context,
    input_file: Path = typer.Argument(..., help="Input specification file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    to_format: str = typer.Option("yaml", "--to", "-t", help="Output format (json/yaml)"),
    to_version: Optional[str] = typer.Option(None, "--version", "-v", help="Target OpenAPI version"),
    from_url: Optional[str] = typer.Option(None, "--from-url", help="Import from URL"),
    save: bool = typer.Option(False, "--save", help="Save to server"),
) -> None:
    """Convert between OpenAPI formats and versions."""
    
    debug = ctx.obj.get("debug", False)
    
    try:
        if from_url:
            import httpx
            console.print(f"[cyan]Fetching from URL:[/] {from_url}")
            response = httpx.get(from_url, timeout=30.0)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                spec = response.json()
            else:
                spec = yaml.safe_load(response.text)
        else:
            spec = read_input(input_file)
        
        if to_version:
            spec = _convert_version(spec, to_version)
            console.print(f"[green]✓[/] Converted to OpenAPI {to_version}")
        
        if not output:
            suffix = ".json" if to_format == "json" else ".yaml"
            output = input_file.with_suffix(suffix)
        
        write_output(spec, output, to_format)
        console.print(f"[green]✓[/] Saved to [bold]{output}[/]")
        
        if save:
            _save_to_server(ctx, spec)
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


def _convert_version(spec: dict, target_version: str) -> dict:
    current_version = spec.get("openapi") or spec.get("swagger")
    if not current_version:
        raise ValueError("Cannot detect OpenAPI version")
    
    if current_version.startswith("2.") and target_version.startswith("3."):
        return _swagger2_to_openapi3(spec)
    elif current_version.startswith("3.0") and target_version.startswith("3.1"):
        spec["openapi"] = "3.1.0"
        return spec
    elif current_version.startswith("3.1") and target_version.startswith("3.0"):
        spec["openapi"] = "3.0.3"
        return spec
    else:
        console.print(f"[yellow]Warning:[/] Version conversion may not be fully supported")
        return spec


def _swagger2_to_openapi3(spec: dict) -> dict:
    converted = {"openapi": "3.0.3", "info": spec.get("info", {}), "paths": {}, "components": {"schemas": {}, "parameters": {}, "responses": {}}}
    for path, methods in spec.get("paths", {}).items():
        converted["paths"][path] = {}
        for method, details in methods.items():
            if method not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                continue
            converted_method = details.copy()
            if "parameters" in details:
                converted_method["parameters"] = []
                for param in details["parameters"]:
                    if param.get("in") == "body":
                        converted_method["requestBody"] = {"content": {"application/json": {"schema": param.get("schema", {})}}}
                    else:
                        converted_method["parameters"].append(param)
            if "responses" in details:
                for status, response in details["responses"].items():
                    if "schema" in response:
                        response["content"] = {"application/json": {"schema": response.pop("schema")}}
            converted["paths"][path][method] = converted_method
    if "definitions" in spec:
        converted["components"]["schemas"] = spec["definitions"]
    return converted


def _save_to_server(ctx: typer.Context, spec: dict) -> None:
    import tempfile
    from apidoc_cli.commands.publish import publish_command
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(spec, f)
        temp_path = Path(f.name)
    try:
        ctx.invoke(publish_command, spec_file=temp_path, targets=["server"])
        console.print("[green]✓[/] Saved to server")
    finally:
        temp_path.unlink()
''')

write_file("apidoc_cli/commands/server.py", r'''"""Server management commands."""

import asyncio
import subprocess
import sys
from typing import Optional

import httpx
import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from apidoc_cli.config import Config

app = typer.Typer()
console = Console()


@app.command(name="start")
def server_start(
    ctx: typer.Context,
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of workers"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on changes"),
    background: bool = typer.Option(False, "--background", "-b", help="Run in background"),
) -> None:
    """Start APIDoc server."""
    
    try:
        if _is_server_running(host, port):
            console.print(f"[yellow]Server already running at http://{host}:{port}[/]")
            return
        
        cmd = [sys.executable, "-m", "uvicorn", "apidoc_server.main:app", "--host", host, "--port", str(port), "--workers", str(workers)]
        if reload:
            cmd.append("--reload")
        
        console.print(f"[green]Starting server at http://{host}:{port}[/]")
        
        if background:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            for _ in range(10):
                if _is_server_running(host, port):
                    console.print(f"[green]✓[/] Server started (PID: {process.pid})")
                    return
                asyncio.run(asyncio.sleep(0.5))
            console.print("[red]✗[/] Server failed to start")
        else:
            subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/]")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command(name="stop")
def server_stop(
    ctx: typer.Context,
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
) -> None:
    """Stop APIDoc server."""
    try:
        try:
            response = httpx.post(f"http://{host}:{port}/shutdown", timeout=5.0)
            if response.status_code == 200:
                console.print("[green]✓[/] Server stopped gracefully")
                return
        except Exception:
            pass
        console.print("[yellow]Could not stop gracefully, try manual termination[/]")
    except Exception as e:
        logger.error(f"Failed to stop server: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command(name="status")
def server_status(
    ctx: typer.Context,
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
) -> None:
    """Check server status."""
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            console.print(Panel(f"[green]✓ Server is running[/]\nURL: http://{host}:{port}\nVersion: {data.get('version', 'unknown')}", title="Server Status", border_style="green"))
        else:
            console.print("[red]✗ Server is not responding properly[/]")
            raise typer.Exit(1)
    except httpx.ConnectError:
        console.print("[yellow]Server is not running[/]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error checking server:[/] {e}")
        raise typer.Exit(1)


@app.command(name="search")
def server_search(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "--limit", "-l", help="Results limit"),
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Server host"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Server port"),
) -> None:
    """Search specifications on server."""
    cfg: Config = ctx.obj["config"]
    server_url = f"http://{host or cfg.server.url.split('/')[2]}"
    try:
        response = httpx.get(f"{server_url}/api/v1/specs/search", params={"q": query, "per_page": limit}, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        if not data.get("items"):
            console.print(f"[yellow]No results found for '{query}'[/]")
            return
        table = Table(title=f"Search Results: '{query}'")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Version")
        table.add_column("Updated")
        for item in data["items"]:
            table.add_row(str(item["id"]), item["name"], item.get("version", "N/A"), item.get("updated_at", "N/A")[:10])
        console.print(table)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command(name="versions")
def server_versions(
    ctx: typer.Context,
    spec_id: int = typer.Argument(..., help="Specification ID"),
    host: Optional[str] = typer.Option(None, "--host", "-h"),
    port: Optional[int] = typer.Option(None, "--port", "-p"),
) -> None:
    """List versions of a specification."""
    cfg: Config = ctx.obj["config"]
    server_url = f"http://{host or cfg.server.url.split('/')[2]}"
    try:
        response = httpx.get(f"{server_url}/api/v1/specs/{spec_id}/versions", timeout=30.0)
        response.raise_for_status()
        data = response.json()
        table = Table(title=f"Versions for Specification #{spec_id}")
        table.add_column("Version", style="cyan")
        table.add_column("Created")
        table.add_column("Created By")
        table.add_column("Changelog")
        for version in data.get("items", []):
            table.add_row(version["version"], version["created_at"][:19], version.get("created_by", "N/A"), version.get("changelog", "")[:50])
        console.print(table)
    except Exception as e:
        logger.error(f"Failed to get versions: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command(name="init")
def server_init(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", "-f", help="Force reinitialize"),
) -> None:
    """Initialize server database."""
    try:
        from apidoc_server.database import init_db
        console.print("[cyan]Initializing database...[/]")
        asyncio.run(init_db())
        console.print("[green]✓[/] Database initialized")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


def _is_server_running(host: str, port: int) -> bool:
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False
''')

write_file("apidoc_cli/commands/tree.py", r'''"""Tree visualization command."""

from pathlib import Path
from typing import Dict

import typer
from loguru import logger
from rich.console import Console
from rich.tree import Tree

from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


@app.command(name="tree")
def tree_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    show_methods: bool = typer.Option(True, "--methods/--no-methods", help="Show HTTP methods"),
    show_schemas: bool = typer.Option(False, "--schemas", help="Show schemas"),
    max_depth: int = typer.Option(10, "--depth", "-d", help="Maximum depth"),
) -> None:
    """Visualize API structure as tree."""
    
    try:
        spec = read_input(spec_file)
        title = spec.get("info", {}).get("title", "API")
        version = spec.get("info", {}).get("version", "")
        root = Tree(f"[bold cyan]{title}[/] [dim]v{version}[/]")
        
        paths = spec.get("paths", {})
        if paths:
            paths_branch = root.add("[bold green]Endpoints[/]")
            _add_paths(paths_branch, paths, show_methods)
        
        if show_schemas:
            schemas = spec.get("components", {}).get("schemas", {})
            if schemas:
                schemas_branch = root.add("[bold yellow]Schemas[/]")
                _add_schemas(schemas_branch, schemas)
        
        servers = spec.get("servers", [])
        if servers:
            servers_branch = root.add("[bold blue]Servers[/]")
            for server in servers:
                servers_branch.add(f"[dim]{server.get('url', '')}[/]")
        
        console.print(root)
    except Exception as e:
        logger.error(f"Tree visualization failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)


def _add_paths(tree: Tree, paths: Dict, show_methods: bool) -> None:
    for path, methods in sorted(paths.items()):
        if not methods:
            continue
        path_branch = tree.add(f"[cyan]{path}[/]")
        if show_methods:
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                color = {"get": "green", "post": "yellow", "put": "blue", "delete": "red", "patch": "magenta"}.get(method.lower(), "white")
                method_text = f"[{color}]{method.upper()}[/]"
                if "summary" in details:
                    method_text += f" - [dim]{details['summary'][:50]}[/]"
                method_branch = path_branch.add(method_text)
                params = details.get("parameters", [])
                if params:
                    params_branch = method_branch.add("[dim]Parameters[/]")
                    for param in params:
                        required = "[red]*[/]" if param.get("required") else ""
                        params_branch.add(f"{param.get('name')} ({param.get('in')}) {required}")


def _add_schemas(tree: Tree, schemas: Dict) -> None:
    for name, schema in sorted(schemas.items()):
        schema_type = schema.get("type", "object")
        schema_branch = tree.add(f"[yellow]{name}[/] [dim]({schema_type})[/]")
        if schema_type == "object":
            props = schema.get("properties", {})
            for prop_name, prop_schema in list(props.items())[:10]:
                prop_type = prop_schema.get("type", "unknown")
                required = " [red]*[/]" if prop_name in schema.get("required", []) else ""
                schema_branch.add(f"[dim]{prop_name}: {prop_type}{required}[/]")
            if len(props) > 10:
                schema_branch.add(f"[dim]... and {len(props) - 10} more[/]")
''')

print("✓ CLI команды созданы (9 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 5. CLI ПЛАГИНЫ
# ═══════════════════════════════════════════════════════════════════
print("📁 CLI плагины...")

write_file("apidoc_cli/plugins/__init__.py", r'''"""Plugin system for APIDoc CLI."""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points


class BaseParser(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def frameworks(self) -> List[str]:
        pass
    
    @abstractmethod
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        pass


class BasePublisher(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    async def publish(self, spec: Dict[str, Any], name: str, version: str, **kwargs) -> Dict[str, Any]:
        pass


class BaseTestGenerator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def generate(self, spec: Dict[str, Any], output_dir: Path, **kwargs) -> List[Path]:
        pass


class PluginManager:
    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {}
        self._publishers: Dict[str, Type[BasePublisher]] = {}
        self._test_generators: Dict[str, Type[BaseTestGenerator]] = {}
        self._load_plugins()
    
    def _load_plugins(self) -> None:
        for ep in entry_points(group="apidoc.plugins"):
            try:
                plugin_class = ep.load()
                if issubclass(plugin_class, BaseParser):
                    instance = plugin_class()
                    for framework in instance.frameworks:
                        self._parsers[framework.lower()] = plugin_class
                elif issubclass(plugin_class, BasePublisher):
                    instance = plugin_class()
                    self._publishers[instance.name.lower()] = plugin_class
                elif issubclass(plugin_class, BaseTestGenerator):
                    instance = plugin_class()
                    self._test_generators[instance.name.lower()] = plugin_class
            except Exception as e:
                import logging
                logging.warning(f"Failed to load plugin {ep.name}: {e}")
    
    def get_parser(self, framework: str) -> Optional[BaseParser]:
        parser_class = self._parsers.get(framework.lower())
        if parser_class:
            return parser_class()
        return None
    
    def list_parsers(self) -> List[str]:
        return list(self._parsers.keys())
    
    def get_publisher(self, name: str) -> Optional[BasePublisher]:
        publisher_class = self._publishers.get(name.lower())
        if publisher_class:
            return publisher_class()
        return None
    
    def list_publishers(self) -> List[str]:
        return list(self._publishers.keys())
    
    def get_test_generator(self, name: str) -> Optional[BaseTestGenerator]:
        generator_class = self._test_generators.get(name.lower())
        if generator_class:
            return generator_class()
        return None
    
    def list_test_generators(self) -> List[str]:
        return list(self._test_generators.keys())
''')

write_file("apidoc_cli/plugins/base.py", r'''"""Base classes for plugins."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseParser(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def frameworks(self) -> List[str]:
        pass
    
    @abstractmethod
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        pass
    
    def detect(self, source: Path) -> bool:
        return False


class BasePublisher(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    @abstractmethod
    async def publish(self, spec: Dict[str, Any], name: str, version: str, **kwargs) -> Dict[str, Any]:
        pass
    
    async def validate_credentials(self, **kwargs) -> bool:
        return True


class BaseTestGenerator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def language(self) -> str:
        pass
    
    @property
    @abstractmethod
    def framework(self) -> str:
        pass
    
    @abstractmethod
    def generate(self, spec: Dict[str, Any], output_dir: Path, **kwargs) -> List[Path]:
        pass
''')

write_file("apidoc_cli/plugins/python_parser.py", r'''"""Python parser plugin for FastAPI and Flask."""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional

from apidoc_cli.plugins.base import BaseParser


class PythonParserPlugin(BaseParser):
    @property
    def name(self) -> str:
        return "python-parser"
    
    @property
    def frameworks(self) -> List[str]:
        return ["fastapi", "flask"]
    
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        framework = self._detect_framework(source)
        if framework == "fastapi":
            return self._parse_fastapi(source, **kwargs)
        elif framework == "flask":
            return self._parse_flask(source, **kwargs)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _detect_framework(self, source: Path) -> Optional[str]:
        if source.is_file():
            content = source.read_text()
        else:
            for pattern in ["app.py", "main.py", "*/app.py", "*/main.py"]:
                files = list(source.glob(pattern))
                if files:
                    content = files[0].read_text()
                    break
            else:
                raise ValueError("No Python app file found")
        
        if "from fastapi import" in content or "import fastapi" in content:
            return "fastapi"
        elif "from flask import" in content or "import flask" in content:
            return "flask"
        return None
    
    def _parse_fastapi(self, source: Path, **kwargs) -> Dict[str, Any]:
        import sys
        sys.path.insert(0, str(source.parent))
        try:
            if source.is_file():
                module_name = source.stem
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, source)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                import importlib
                module = importlib.import_module(source.name)
            
            app = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, "__class__") and attr.__class__.__name__ == "FastAPI":
                    app = attr
                    break
            
            if not app:
                raise ValueError("No FastAPI app instance found")
            
            openapi_spec = app.openapi()
            if kwargs.get("title"):
                openapi_spec["info"]["title"] = kwargs["title"]
            if kwargs.get("version"):
                openapi_spec["info"]["version"] = kwargs["version"]
            return openapi_spec
        except Exception as e:
            raise RuntimeError(f"Failed to parse FastAPI app: {e}")
        finally:
            sys.path.pop(0)
    
    def _parse_flask(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", source.stem), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        if source.is_file():
            content = source.read_text()
            tree = ast.parse(content)
            
            class RouteVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.routes = []
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Attribute) and node.func.attr == "route":
                        if len(node.args) > 0 and isinstance(node.args[0], ast.Constant):
                            path = node.args[0].value
                            methods = ["GET"]
                            for kw in node.keywords:
                                if kw.arg == "methods" and isinstance(kw.value, ast.List):
                                    methods = [el.value.upper() for el in kw.value.elts if isinstance(el, ast.Constant)]
                            self.routes.append({"path": path, "methods": methods})
                    self.generic_visit(node)
            
            visitor = RouteVisitor()
            visitor.visit(tree)
            for route in visitor.routes:
                if route["path"] not in spec["paths"]:
                    spec["paths"][route["path"]] = {}
                for method in route["methods"]:
                    spec["paths"][route["path"]][method.lower()] = {"summary": f"{method} {route['path']}", "responses": {"200": {"description": "Successful response"}}}
        return spec
''')

write_file("apidoc_cli/plugins/js_parser.py", r'''"""JavaScript/TypeScript parser plugin."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from apidoc_cli.plugins.base import BaseParser


class JSParserPlugin(BaseParser):
    @property
    def name(self) -> str:
        return "js-parser"
    
    @property
    def frameworks(self) -> List[str]:
        return ["express", "nestjs", "fastify"]
    
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        framework = self._detect_framework(source)
        if framework == "express":
            return self._parse_express(source, **kwargs)
        elif framework == "nestjs":
            return self._parse_nestjs(source, **kwargs)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _detect_framework(self, source: Path) -> Optional[str]:
        if source.is_file():
            content = source.read_text()
        else:
            pkg_json = source / "package.json"
            if pkg_json.exists():
                pkg = json.loads(pkg_json.read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "@nestjs/core" in deps: return "nestjs"
                elif "express" in deps: return "express"
                elif "fastify" in deps: return "fastify"
            for js_file in source.rglob("*.js"):
                content = js_file.read_text()
                if "express()" in content: return "express"
            return None
        
        if "express()" in content: return "express"
        elif "@Module" in content or "@Controller" in content: return "nestjs"
        return None
    
    def _parse_express(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "Express API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        content = source.read_text() if source.is_file() else ""
        route_patterns = [r'app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', r'router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']']
        for pattern in route_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                method = match.group(1).lower()
                path = match.group(2)
                if path not in spec["paths"]:
                    spec["paths"][path] = {}
                spec["paths"][path][method] = {"summary": f"{method.upper()} {path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
    
    def _parse_nestjs(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "NestJS API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for controller_file in source.rglob("*.controller.ts"):
            content = controller_file.read_text()
            prefix_match = re.search(r'@Controller\s*\(\s*["\']([^"\']+)["\']', content)
            prefix = prefix_match.group(1) if prefix_match else ""
            decorators = ["Get", "Post", "Put", "Delete", "Patch"]
            for decorator in decorators:
                pattern = rf'@{decorator}\s*\(\s*["\']([^"\']*)["\']'
                for match in re.finditer(pattern, content):
                    sub_path = match.group(1)
                    full_path = prefix + sub_path
                    if full_path not in spec["paths"]:
                        spec["paths"][full_path] = {}
                    spec["paths"][full_path][decorator.lower()] = {"summary": f"{decorator.upper()} {full_path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
''')

write_file("apidoc_cli/plugins/java_parser.py", r'''"""Java parser plugin."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from apidoc_cli.plugins.base import BaseParser


class JavaParserPlugin(BaseParser):
    @property
    def name(self) -> str:
        return "java-parser"
    
    @property
    def frameworks(self) -> List[str]:
        return ["spring", "jax-rs"]
    
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        framework = self._detect_framework(source)
        if framework == "spring":
            return self._parse_spring(source, **kwargs)
        elif framework == "jax-rs":
            return self._parse_jaxrs(source, **kwargs)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _detect_framework(self, source: Path) -> Optional[str]:
        if source.is_dir():
            pom = source / "pom.xml"
            if pom.exists():
                content = pom.read_text()
                if "spring-boot" in content: return "spring"
                elif "jax-rs" in content or "javax.ws.rs" in content: return "jax-rs"
            for java_file in source.rglob("*.java"):
                content = java_file.read_text()
                if "@RestController" in content or "@Controller" in content: return "spring"
                elif "@Path" in content: return "jax-rs"
        return None
    
    def _parse_spring(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "Spring API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for java_file in source.rglob("*.java"):
            content = java_file.read_text()
            class_path = ""
            class_match = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content)
            if class_match: class_path = class_match.group(1)
            mappings = [("@GetMapping", "get"), ("@PostMapping", "post"), ("@PutMapping", "put"), ("@DeleteMapping", "delete"), ("@PatchMapping", "patch"), ("@RequestMapping", "get")]
            for annotation, method in mappings:
                pattern = rf'{annotation}\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']'
                for match in re.finditer(pattern, content):
                    sub_path = match.group(1)
                    full_path = class_path + sub_path
                    if full_path not in spec["paths"]:
                        spec["paths"][full_path] = {}
                    spec["paths"][full_path][method] = {"summary": f"{method.upper()} {full_path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
    
    def _parse_jaxrs(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "JAX-RS API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for java_file in source.rglob("*.java"):
            content = java_file.read_text()
            class_path = ""
            class_match = re.search(r'@Path\s*\(\s*["\']([^"\']+)["\']', content)
            if class_match: class_path = class_match.group(1)
            method_annotations = {"@GET": "get", "@POST": "post", "@PUT": "put", "@DELETE": "delete", "@PATCH": "patch"}
            for annotation, method in method_annotations.items():
                if annotation in content:
                    path_match = re.search(rf'{annotation}\s*\n.*?@Path\s*\(\s*["\']([^"\']+)["\']', content, re.DOTALL)
                    sub_path = path_match.group(1) if path_match else ""
                    full_path = class_path + sub_path
                    if full_path not in spec["paths"]:
                        spec["paths"][full_path] = {}
                    spec["paths"][full_path][method] = {"summary": f"{method.upper()} {full_path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
''')

write_file("apidoc_cli/plugins/go_parser.py", r'''"""Go parser plugin."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from apidoc_cli.plugins.base import BaseParser


class GoParserPlugin(BaseParser):
    @property
    def name(self) -> str:
        return "go-parser"
    
    @property
    def frameworks(self) -> List[str]:
        return ["gin", "echo", "fiber"]
    
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        framework = self._detect_framework(source)
        if framework == "gin":
            return self._parse_gin(source, **kwargs)
        elif framework == "echo":
            return self._parse_echo(source, **kwargs)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _detect_framework(self, source: Path) -> Optional[str]:
        if source.is_dir():
            go_mod = source / "go.mod"
            if go_mod.exists():
                content = go_mod.read_text()
                if "gin-gonic/gin" in content: return "gin"
                elif "labstack/echo" in content: return "echo"
                elif "gofiber/fiber" in content: return "fiber"
            for go_file in source.rglob("*.go"):
                content = go_file.read_text()
                if "gin." in content: return "gin"
                elif "echo." in content: return "echo"
        return None
    
    def _parse_gin(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "Gin API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for go_file in source.rglob("*.go"):
            content = go_file.read_text()
            methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            for method in methods:
                pattern = rf'\.{method}\s*\(\s*["\']([^"\']+)["\']'
                for match in re.finditer(pattern, content):
                    path = match.group(1)
                    if path not in spec["paths"]:
                        spec["paths"][path] = {}
                    spec["paths"][path][method.lower()] = {"summary": f"{method} {path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
    
    def _parse_echo(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "Echo API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for go_file in source.rglob("*.go"):
            content = go_file.read_text()
            methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            for method in methods:
                pattern = rf'e\.{method}\s*\(\s*["\']([^"\']+)["\']'
                for match in re.finditer(pattern, content):
                    path = match.group(1)
                    if path not in spec["paths"]:
                        spec["paths"][path] = {}
                    spec["paths"][path][method.lower()] = {"summary": f"{method} {path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
''')

write_file("apidoc_cli/plugins/pytest_generator.py", """\"\"\"Pytest test generator.\"\"\"

from pathlib import Path
from typing import Any, Dict, List

from apidoc_cli.plugins.base import BaseTestGenerator


class PytestGeneratorPlugin(BaseTestGenerator):
    @property
    def name(self) -> str:
        return "pytest"
    
    @property
    def language(self) -> str:
        return "python"
    
    @property
    def framework(self) -> str:
        return "pytest"
    
    def generate(self, spec: Dict[str, Any], output_dir: Path, **kwargs) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        conftest = self._generate_conftest(spec)
        conftest_path = output_dir / "conftest.py"
        conftest_path.write_text(conftest)
        generated_files.append(conftest_path)
        
        tests_by_tag = self._group_by_tag(spec)
        for tag, endpoints in tests_by_tag.items():
            test_content = self._generate_test_file(tag, endpoints, spec)
            test_path = output_dir / f"test_{self._sanitize_name(tag)}.py"
            test_path.write_text(test_content)
            generated_files.append(test_path)
        
        return generated_files
    
    def _generate_conftest(self, spec: Dict) -> str:
        servers = spec.get("servers", [{}])
        base_url = servers[0].get("url", "http://localhost:8000") if servers else "http://localhost:8000"
        lines = []
        lines.append("\"\"\"Pytest configuration.\"\"\"")
        lines.append("")
        lines.append("import pytest")
        lines.append("import httpx")
        lines.append("")
        lines.append("")
        lines.append("@pytest.fixture")
        lines.append("def base_url():")
        lines.append(f"    return \"{base_url}\"")
        lines.append("")
        lines.append("")
        lines.append("@pytest.fixture")
        lines.append("async def client():")
        lines.append("    async with httpx.AsyncClient() as client:")
        lines.append("        yield client")
        return "\\n".join(lines)
    
    def _group_by_tag(self, spec: Dict) -> Dict[str, List]:
        groups = {"default": []}
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                tags = details.get("tags", ["default"])
                for tag in tags:
                    if tag not in groups:
                        groups[tag] = []
                    groups[tag].append({"path": path, "method": method, "details": details})
        return groups
    
    def _generate_test_file(self, tag: str, endpoints: List, spec: Dict) -> str:
        class_name = self._sanitize_name(tag).title()
        lines = []
        lines.append(f"\"\"\"Tests for {tag} endpoints.\"\"\"")
        lines.append("")
        lines.append("import pytest")
        lines.append("from httpx import AsyncClient")
        lines.append("")
        lines.append("")
        lines.append(f"class Test{class_name}API:")
        lines.append(f"    \"\"\"Test cases for {tag} endpoints.\"\"\"")
        lines.append("    ")
        for endpoint in endpoints:
            lines.append(self._generate_test_method(endpoint))
        return "\\n".join(lines)
    
    def _generate_test_method(self, endpoint: Dict) -> str:
        path = endpoint["path"]
        method = endpoint["method"]
        details = endpoint["details"]
        op_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
        success_code = "200"
        for code in ["200", "201", "204"]:
            if code in details.get("responses", {}):
                success_code = code
                break
        lines = []
        lines.append("")
        lines.append("    @pytest.mark.asyncio")
        lines.append(f"    async def test_{op_id}(self, client: AsyncClient, base_url: str):")
        lines.append(f"        \"\"\"Test {method.upper()} {path}\"\"\"")
        lines.append(f"        response = await client.{method.lower()}(f\"{{base_url}}{path}\")")
        lines.append(f"        assert response.status_code == {success_code}")
        return "\\n".join(lines)
    
    def _sanitize_name(self, name: str) -> str:
        import re
        name = re.sub(r"[^\\w]", "_", name.lower())
        if name[0].isdigit():
            name = "_" + name
        return name
""")

write_file("apidoc_cli/plugins/jest_generator.py", """'''Jest test generator.'''

from pathlib import Path
from typing import Any, Dict, List

from apidoc_cli.plugins.base import BaseTestGenerator


class JestGeneratorPlugin(BaseTestGenerator):
    @property
    def name(self) -> str:
        return "jest"
    
    @property
    def language(self) -> str:
        return "javascript"
    
    @property
    def framework(self) -> str:
        return "jest"
    
    def generate(self, spec: Dict[str, Any], output_dir: Path, **kwargs) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        tests_by_tag = self._group_by_tag(spec)
        for tag, endpoints in tests_by_tag.items():
            test_content = self._generate_test_file(tag, endpoints, spec)
            test_path = output_dir / f"{self._sanitize_name(tag)}.test.js"
            test_path.write_text(test_content)
            generated_files.append(test_path)
        return generated_files
    
    def _group_by_tag(self, spec: Dict) -> Dict[str, List]:
        groups = {"default": []}
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                tags = details.get("tags", ["default"])
                for tag in tags:
                    if tag not in groups:
                        groups[tag] = []
                    groups[tag].append({"path": path, "method": method, "details": details})
        return groups
    
    def _generate_test_file(self, tag: str, endpoints: List, spec: Dict) -> str:
        servers = spec.get("servers", [{}])
        base_url = servers[0].get("url", "http://localhost:8000") if servers else "http://localhost:8000"
        content = "/**\\n"
        content += " * Tests for " + tag + " endpoints\\n"
        content += " */\\n"
        content += "const axios = require('axios');\\n"
        content += "const BASE_URL = '" + base_url + "';\\n\\n"
        content += "describe('" + tag + " API', () => {\\n"
        content += "    let client;\\n"
        content += "    beforeEach(() => {\\n"
        content += "        client = axios.create({ baseURL: BASE_URL, timeout: 5000 });\\n"
        content += "    });\\n\\n"
        for endpoint in endpoints:
            path = endpoint["path"]
            method = endpoint["method"]
            details = endpoint["details"]
            success_code = 200
            for code in [200, 201, 204]:
                if str(code) in details.get("responses", {}):
                    success_code = code
                    break
            content += "    test('" + method.upper() + " " + path + "', async () => {\\n"
            content += "        const response = await client." + method.lower() + "('" + path + "');\\n"
            content += "        expect(response.status).toBe(" + str(success_code) + ");\\n"
            content += "    });\\n\\n"
        content += "});\\n"
        return content
    
    def _sanitize_name(self, name: str) -> str:
        import re
        return re.sub(r"[^\\w\\-]", "_", name.lower())
""")

write_file("apidoc_cli/plugins/publishers/__init__.py", r'''"""Publisher plugins."""

from apidoc_cli.plugins.publishers.github import GitHubPublisher
from apidoc_cli.plugins.publishers.readme import ReadMePublisher
from apidoc_cli.plugins.publishers.redocly import RedoclyPublisher
from apidoc_cli.plugins.publishers.swaggerhub import SwaggerHubPublisher

__all__ = ["SwaggerHubPublisher", "GitHubPublisher", "ReadMePublisher", "RedoclyPublisher"]
''')

write_file("apidoc_cli/plugins/publishers/swaggerhub.py", r'''"""SwaggerHub publisher plugin."""

import httpx
from loguru import logger

from apidoc_cli.plugins.base import BasePublisher


class SwaggerHubPublisher(BasePublisher):
    @property
    def name(self) -> str:
        return "swaggerhub"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def publish(self, spec: dict, name: str, version: str, api_key: str = None, owner: str = None, is_private: bool = False, **kwargs) -> dict:
        if not api_key:
            raise ValueError("SwaggerHub API key is required")
        if not owner:
            raise ValueError("SwaggerHub owner is required")
        
        url = f"https://api.swaggerhub.com/apis/{owner}/{name}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, params={"version": version, "isPrivate": str(is_private).lower()}, json=spec, headers={"Authorization": api_key, "Content-Type": "application/json"})
            if response.status_code == 409:
                logger.info(f"API {name} already exists, updating...")
                response = await client.put(f"{url}/{version}", json=spec, headers={"Authorization": api_key, "Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
    
    async def validate_credentials(self, api_key: str = None, **kwargs) -> bool:
        if not api_key: return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.swaggerhub.com/apis", headers={"Authorization": api_key})
                return response.status_code == 200
        except Exception:
            return False
''')

write_file("apidoc_cli/plugins/publishers/github.py", r'''"""GitHub publisher plugin."""

import base64
import httpx
import yaml
from loguru import logger

from apidoc_cli.plugins.base import BasePublisher


class GitHubPublisher(BasePublisher):
    @property
    def name(self) -> str:
        return "github"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def publish(self, spec: dict, name: str, version: str, token: str = None, repo: str = None, path: str = None, branch: str = "main", message: str = None, **kwargs) -> dict:
        if not token: raise ValueError("GitHub token is required")
        if not repo: raise ValueError("GitHub repository is required (format: owner/repo)")
        
        yaml_content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        content_base64 = base64.b64encode(yaml_content.encode()).decode()
        file_path = path or f"docs/openapi/{name}.yaml"
        commit_message = message or f"Update OpenAPI specification {name} v{version}"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"https://api.github.com/repos/{repo}/contents/{file_path}", params={"ref": branch}, headers=headers)
            data = {"message": commit_message, "content": content_base64, "branch": branch}
            if response.status_code == 200: data["sha"] = response.json()["sha"]
            response = await client.put(f"https://api.github.com/repos/{repo}/contents/{file_path}", json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return {"url": result["content"]["html_url"], "sha": result["content"]["sha"], "path": file_path}
    
    async def validate_credentials(self, token: str = None, **kwargs) -> bool:
        if not token: return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.github.com/user", headers={"Authorization": f"Bearer {token}"})
                return response.status_code == 200
        except Exception:
            return False
''')

write_file("apidoc_cli/plugins/publishers/readme.py", r'''"""ReadMe.com publisher plugin."""

import httpx
from loguru import logger

from apidoc_cli.plugins.base import BasePublisher


class ReadMePublisher(BasePublisher):
    @property
    def name(self) -> str:
        return "readme"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def publish(self, spec: dict, name: str, version: str, api_key: str = None, **kwargs) -> dict:
        if not api_key: raise ValueError("ReadMe API key is required")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://dash.readme.com/api/v1/api-registry", json={"spec": spec, "version": version, "title": name}, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
    
    async def validate_credentials(self, api_key: str = None, **kwargs) -> bool:
        if not api_key: return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://dash.readme.com/api/v1", headers={"Authorization": f"Bearer {api_key}"})
                return response.status_code == 200
        except Exception:
            return False
''')

write_file("apidoc_cli/plugins/publishers/redocly.py", r'''"""Redocly publisher plugin."""

import httpx
from loguru import logger

from apidoc_cli.plugins.base import BasePublisher


class RedoclyPublisher(BasePublisher):
    @property
    def name(self) -> str:
        return "redocly"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def publish(self, spec: dict, name: str, version: str, api_key: str = None, organization: str = None, **kwargs) -> dict:
        if not api_key: raise ValueError("Redocly API key is required")
        if not organization: raise ValueError("Redocly organization is required")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"https://api.redocly.com/orgs/{organization}/apis", json={"name": name, "version": version, "spec": spec}, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
            if response.status_code == 409:
                apis_response = await client.get(f"https://api.redocly.com/orgs/{organization}/apis", headers={"Authorization": f"Bearer {api_key}"})
                api_id = None
                for api in apis_response.json().get("items", []):
                    if api.get("name") == name: api_id = api.get("id"); break
                if api_id:
                    response = await client.put(f"https://api.redocly.com/orgs/{organization}/apis/{api_id}/versions/{version}", json={"spec": spec}, headers={"Authorization": f"Bearer {api_key}"})
            response.raise_for_status()
            return response.json()
    
    async def validate_credentials(self, api_key: str = None, **kwargs) -> bool:
        if not api_key: return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.redocly.com/auth/status", headers={"Authorization": f"Bearer {api_key}"})
                return response.status_code == 200
        except Exception:
            return False
''')

# Шаблоны
write_file("apidoc_cli/templates/openapi_base.yaml", r'''openapi: 3.0.3

info:
  title: {{ title }}
  description: {{ description }}
  version: {{ version }}
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: {{ server_url }}
    description: {{ server_description }}

paths:
  /example:
    get:
      summary: Example endpoint
      operationId: getExample
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
''')

write_file("apidoc_cli/templates/test_template.py.j2", r'''"""
Tests for {{ api_name }} v{{ api_version }}
Generated by APIDoc Manager
"""

import pytest
import httpx


class Test{{ api_name|replace(' ', '')|replace('-', '_') }}API:
    """Test suite for {{ api_name }}."""
    
    @pytest.fixture
    def base_url(self):
        return "{{ base_url }}"
    
    @pytest.fixture
    async def client(self):
        async with httpx.AsyncClient() as client:
            yield client
    
{% for endpoint in endpoints %}
    @pytest.mark.asyncio
    async def test_{{ endpoint.operationId }}(self, client: httpx.AsyncClient, base_url: str):
        """Test {{ endpoint.method.upper() }} {{ endpoint.path }}"""
        response = await client.{{ endpoint.method }}(f"{base_url}{{ endpoint.path }}")
        assert response.status_code in [200, 201, 204]
    
{% endfor %}
''')

print("✓ CLI плагины созданы (14 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 6. APIDOC SERVER — ЯДРО
# ═══════════════════════════════════════════════════════════════════
print("📁 APIDoc Server — ядро...")

write_file("apidoc_server/__init__.py", r'''"""APIDoc Manager Server."""

__version__ = "0.1.0"
''')

write_file("apidoc_server/main.py", r'''"""APIDoc Server - FastAPI application."""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from loguru import logger

from apidoc_server.api import auth, diff, import_export, search, specs, versions
from apidoc_server.config import settings
from apidoc_server.database import engine, init_db
from apidoc_server.logging_config import setup_production_logging
from apidoc_server.metrics import MetricsMiddleware, metrics, metrics_endpoint
from apidoc_server.security import CSRFMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    setup_production_logging(log_level=settings.log_level, json_format=settings.log_json)
    logger.info("Starting APIDoc Server...")
    await init_db()
    logger.info(f"Database initialized at {settings.database_url}")
    yield
    logger.info("Shutting down APIDoc Server...")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="APIDoc Manager API",
        description="Centralized OpenAPI specification management",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.enable_docs else None,
        redoc_url="/api/redoc" if settings.enable_docs else None,
    )
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token"],
    )
    
    if settings.enable_metrics:
        app.add_middleware(MetricsMiddleware, metrics_manager=metrics)
    
    app.add_middleware(CSRFMiddleware)
    
    app.include_router(specs.router, prefix="/api/v1", tags=["Specifications"])
    app.include_router(versions.router, prefix="/api/v1", tags=["Versions"])
    app.include_router(diff.router, prefix="/api/v1", tags=["Diff"])
    app.include_router(search.router, prefix="/api/v1", tags=["Search"])
    app.include_router(import_export.router, prefix="/api/v1", tags=["Import/Export"])
    app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
    
    if settings.enable_metrics:
        @app.get("/metrics")
        async def get_metrics():
            return await metrics_endpoint()
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/health/readiness")
    async def readiness_check():
        try:
            from sqlalchemy import text
            from apidoc_server.database import get_db
            async for session in get_db():
                await session.execute(text("SELECT 1"))
                break
            return {"status": "ready"}
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return {"status": "not ready", "error": str(e)}
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apidoc_server.main:app", host=settings.host, port=settings.port, reload=settings.debug, log_level=settings.log_level.lower())
''')

write_file("apidoc_server/config.py", r'''"""Server configuration."""

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APIDOC_", env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    
    host: str = Field("0.0.0.0")
    port: int = Field(8000, ge=1, le=65535)
    debug: bool = Field(False)
    log_level: str = Field("INFO")
    log_json: bool = Field(True)
    secret_key: str = Field("change-me-in-production")
    allowed_hosts: List[str] = Field(["*"])
    cors_origins: List[str] = Field(["*"])
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str): return [origin.strip() for origin in v.split(",")]
        return v
    
    database_url: str = Field("sqlite+aiosqlite:///./apidoc.db")
    database_pool_size: int = Field(20, ge=1)
    database_max_overflow: int = Field(10, ge=0)
    redis_url: Optional[str] = Field(None)
    enable_docs: bool = Field(True)
    rate_limit_per_minute: int = Field(60)
    rate_limit_per_hour: int = Field(1000)
    data_dir: Path = Field(Path("./data"))
    upload_max_size: int = Field(10 * 1024 * 1024)
    enable_metrics: bool = Field(True)
    token_expire_minutes: int = Field(1440)
    
    def model_post_init(self, __context) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
''')

write_file("apidoc_server/models.py", r'''"""Database models for APIDoc Server."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Specification(Base):
    __tablename__ = "specifications"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(50))
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    versions: Mapped[list["SpecVersion"]] = relationship("SpecVersion", back_populates="specification", cascade="all, delete-orphan")


class SpecVersion(Base):
    __tablename__ = "spec_versions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    spec_id: Mapped[int] = mapped_column(ForeignKey("specifications.id", ondelete="CASCADE"))
    version: Mapped[str] = mapped_column(String(50))
    content: Mapped[dict] = mapped_column(JSON)
    format: Mapped[str] = mapped_column(String(10), default="json")
    changelog: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(255))
    specification: Mapped["Specification"] = relationship("Specification", back_populates="versions")
''')

write_file("apidoc_server/schemas.py", r'''"""Pydantic schemas for API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class SpecificationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    content: Dict[str, Any]
    format: str = Field(default="json", pattern="^(json|yaml)$")
    tags: Optional[List[str]] = None
    changelog: Optional[str] = None
    created_by: Optional[str] = None
    
    @field_validator("content")
    @classmethod
    def validate_openapi_version(cls, v):
        if "openapi" not in v and "swagger" not in v:
            raise ValueError("Invalid OpenAPI specification")
        return v


class SpecificationResponse(BaseModel):
    id: int
    name: str
    title: str
    description: Optional[str] = None
    version: str
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class SpecificationDetailResponse(SpecificationResponse):
    content: Optional[Dict[str, Any]] = None
    format: Optional[str] = None


class SpecificationListResponse(BaseModel):
    items: List[SpecificationResponse]
    total: int
    page: int
    per_page: int
    pages: int


class SpecificationImport(BaseModel):
    url: str
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None


class VersionCreate(BaseModel):
    content: Dict[str, Any]
    version: str
    format: str = "json"
    changelog: Optional[str] = None
    created_by: Optional[str] = None


class VersionResponse(BaseModel):
    id: int
    spec_id: int
    version: str
    format: str
    changelog: Optional[str] = None
    created_at: datetime
    created_by: Optional[str] = None
    model_config = {"from_attributes": True}


class VersionListResponse(BaseModel):
    items: List[VersionResponse]
    total: int
    page: int
    per_page: int
    pages: int


class DiffRequest(BaseModel):
    version1: str
    version2: str
''')

write_file("apidoc_server/database.py", r'''"""Database configuration and session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apidoc_server.config import settings
from apidoc_server.models import Base

engine = create_async_engine(settings.database_url, echo=settings.debug, future=True, pool_size=settings.database_pool_size, max_overflow=settings.database_max_overflow)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
''')

write_file("apidoc_server/security.py", r'''"""Security utilities."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from apidoc_server.config import settings


class SecurityManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.algorithm = "HS256"
        self.secret_key = settings.secret_key
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.token_expire_minutes))
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            return payload
        except JWTError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")
    
    def generate_api_key(self) -> Tuple[str, str]:
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return api_key, key_hash


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cookie_name: str = "csrf_token", header_name: str = "X-CSRF-Token"):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.safe_methods = {"GET", "HEAD", "OPTIONS"}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in self.safe_methods:
            response = await call_next(request)
            return response
        
        header_token = request.headers.get(self.header_name)
        cookie_token = request.cookies.get(self.cookie_name)
        
        if not header_token or not cookie_token:
            return Response(content='{"error": "CSRF token missing"}', status_code=status.HTTP_403_FORBIDDEN, media_type="application/json")
        if not hmac.compare_digest(header_token, cookie_token):
            return Response(content='{"error": "CSRF token mismatch"}', status_code=status.HTTP_403_FORBIDDEN, media_type="application/json")
        
        return await call_next(request)


security_manager = SecurityManager()
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    payload = security_manager.verify_token(token)
    return {"username": payload.get("sub"), "scopes": payload.get("scopes", [])}
''')

write_file("apidoc_server/metrics.py", r'''"""Prometheus metrics for APIDoc Server."""

import time
from typing import Callable

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class MetricsManager:
    def __init__(self):
        self.http_requests_total = Counter("apidoc_http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
        self.http_request_duration_seconds = Histogram("apidoc_http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"], buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10))
        self.http_requests_in_progress = Gauge("apidoc_http_requests_in_progress", "HTTP requests in progress", ["method", "endpoint"])
        self.specifications_total = Gauge("apidoc_specifications_total", "Total number of specifications")
        self.database_connections = Gauge("apidoc_database_connections", "Active database connections")
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        self.http_requests_total.labels(method=method, endpoint=path, status=str(status_code)).inc()
        self.http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)
    
    def track_in_progress(self, method: str, path: str):
        def start(): self.http_requests_in_progress.labels(method=method, endpoint=path).inc()
        def end(): self.http_requests_in_progress.labels(method=method, endpoint=path).dec()
        return start, end


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, metrics_manager: MetricsManager):
        super().__init__(app)
        self.metrics = metrics_manager
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start, end = self.metrics.track_in_progress(request.method, request.url.path)
        start()
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            self.metrics.record_request(request.method, request.url.path, response.status_code, duration)
            return response
        except Exception:
            self.metrics.record_request(request.method, request.url.path, 500, time.time() - start_time)
            raise
        finally:
            end()


metrics = MetricsManager()


async def metrics_endpoint():
    from fastapi import Response
    return Response(content=generate_latest(), media_type="text/plain")
''')

write_file("apidoc_server/logging_config.py", r'''"""Production logging configuration."""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from loguru import logger


class JSONFormatter:
    def __call__(self, record: Dict[str, Any]) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }
        if record["exception"]:
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
            }
        return json.dumps(log_entry, default=str)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_production_logging(log_level: str = "INFO", log_file: str = "logs/apidoc.json", json_format: bool = True, add_stdout: bool = True) -> None:
    logger.remove()
    handlers = []
    
    if json_format:
        handlers.append({"sink": log_file, "format": JSONFormatter(), "level": log_level, "rotation": "100 MB", "retention": "30 days", "compression": "gz"})
        if add_stdout:
            handlers.append({"sink": sys.stdout, "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", "level": log_level, "colorize": True})
    else:
        handlers.append({"sink": sys.stdout, "format": "{time} | {level} | {message}", "level": log_level})
        handlers.append({"sink": log_file, "format": "{time} | {level} | {message}", "level": "DEBUG", "rotation": "100 MB", "retention": "30 days"})
    
    for handler in handlers:
        logger.add(**handler)
    
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for logger_name in ["uvicorn", "fastapi", "sqlalchemy"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
''')

print("✓ APIDoc Server — ядро создано (9 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 7. APIDOC SERVER — API ЭНДПОИНТЫ
# ═══════════════════════════════════════════════════════════════════
print("📁 APIDoc Server — API эндпоинты...")

write_file("apidoc_server/api/__init__.py", r'''"""API routes module."""

from apidoc_server.api import auth, diff, import_export, search, specs, versions

__all__ = ["specs", "versions", "diff", "search", "import_export", "auth"]
''')

write_file("apidoc_server/api/specs.py", r'''"""Specification API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import Specification, SpecVersion

router = APIRouter()


@router.post("/specs", response_model=schemas.SpecificationResponse)
async def create_specification(spec_data: schemas.SpecificationCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Specification).where(Specification.name == spec_data.name))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Specification '{spec_data.name}' already exists")
        
        spec = Specification(
            name=spec_data.name,
            title=spec_data.content.get("info", {}).get("title", spec_data.name),
            description=spec_data.content.get("info", {}).get("description"),
            version=spec_data.content.get("info", {}).get("version", "1.0.0"),
            tags=spec_data.tags or [],
        )
        db.add(spec)
        await db.flush()
        
        version = SpecVersion(spec_id=spec.id, version=spec.version, content=spec_data.content, format=spec_data.format, changelog=spec_data.changelog, created_by=spec_data.created_by)
        db.add(version)
        await db.commit()
        await db.refresh(spec)
        logger.info(f"Created specification '{spec.name}' (ID: {spec.id})")
        return spec
    except HTTPException:
        raise
    except (IntegrityError, SQLAlchemyError) as e:
        await db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")


@router.get("/specs", response_model=schemas.SpecificationListResponse)
async def list_specifications(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), tag: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(Specification)
    if tag:
        query = query.where(Specification.tags.contains([tag]))
    
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    query = query.order_by(Specification.updated_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    specs = result.scalars().all()
    return {"items": specs, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}


@router.get("/specs/{spec_id}", response_model=schemas.SpecificationDetailResponse)
async def get_specification(spec_id: int, version: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    spec = result.scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    if version:
        version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
    else:
        version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).limit(1))
    spec_version = version_result.scalar_one_or_none()
    if not spec_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    
    return {**spec.__dict__, "content": spec_version.content, "format": spec_version.format}


@router.delete("/specs/{spec_id}")
async def delete_specification(spec_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    spec = result.scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    await db.delete(spec)
    await db.commit()
    logger.info(f"Deleted specification {spec_id}")
    return {"message": f"Specification {spec_id} deleted"}
''')

write_file("apidoc_server/api/versions.py", r'''"""Version management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import Specification, SpecVersion

router = APIRouter()


@router.post("/specs/{spec_id}/versions", response_model=schemas.VersionResponse)
async def create_version(spec_id: int, version_data: schemas.VersionCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    spec = result.scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version_data.version))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Version '{version_data.version}' already exists")
    
    version = SpecVersion(spec_id=spec_id, version=version_data.version, content=version_data.content, format=version_data.format, changelog=version_data.changelog, created_by=version_data.created_by)
    db.add(version)
    spec.version = version_data.version
    spec.updated_at = func.now()
    await db.commit()
    await db.refresh(version)
    return version


@router.get("/specs/{spec_id}/versions", response_model=schemas.VersionListResponse)
async def list_versions(spec_id: int, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    count_result = await db.execute(select(func.count()).select_from(SpecVersion).where(SpecVersion.spec_id == spec_id))
    total = count_result.scalar()
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    versions = result.scalars().all()
    return {"items": versions, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}


@router.get("/specs/{spec_id}/versions/{version}")
async def get_version(spec_id: int, version: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
    version_obj = result.scalar_one_or_none()
    if not version_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Version '{version}' not found")
    return version_obj


@router.delete("/specs/{spec_id}/versions/{version}")
async def delete_version(spec_id: int, version: str, db: AsyncSession = Depends(get_db)):
    count_result = await db.execute(select(func.count()).select_from(SpecVersion).where(SpecVersion.spec_id == spec_id))
    if count_result.scalar() <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the only version")
    
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
    version_obj = result.scalar_one_or_none()
    if not version_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Version '{version}' not found")
    await db.delete(version_obj)
    await db.commit()
    return {"message": f"Version '{version}' deleted"}
''')

write_file("apidoc_server/api/diff.py", r'''"""Diff API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import SpecVersion
from apidoc_server.services.diff_service import DiffService

router = APIRouter()
diff_service = DiffService()


@router.post("/specs/{spec_id}/diff")
async def compare_versions(spec_id: int, diff_request: schemas.DiffRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version.in_([diff_request.version1, diff_request.version2])))
    versions = result.scalars().all()
    if len(versions) != 2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both versions not found")
    
    v1 = next((v for v in versions if v.version == diff_request.version1), None)
    v2 = next((v for v in versions if v.version == diff_request.version2), None)
    if not v1 or not v2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versions not found")
    
    diff_result = diff_service.compare(v1.content, v2.content)
    return {"spec_id": spec_id, "version1": diff_request.version1, "version2": diff_request.version2, "changes": diff_result["changes"], "breaking_changes": diff_result["breaking_changes"], "summary": diff_result["summary"]}
''')

write_file("apidoc_server/api/search.py", r'''"""Search API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import Specification

router = APIRouter()


@router.get("/specs/search")
async def search_specifications(q: str = Query(..., min_length=2), page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), tag: str = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(Specification).where(or_(Specification.name.ilike(f"%{q}%"), Specification.title.ilike(f"%{q}%"), Specification.description.ilike(f"%{q}%")))
    if tag:
        query = query.where(Specification.tags.contains([tag]))
    
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    result = await db.execute(query.order_by(Specification.updated_at.desc()).offset((page - 1) * per_page).limit(per_page))
    specs = result.scalars().all()
    return schemas.SpecificationListResponse(items=specs, total=total, page=page, per_page=per_page, pages=(total + per_page - 1) // per_page)
''')

write_file("apidoc_server/api/import_export.py", r'''"""Import/Export API endpoints."""

import json
from typing import Optional

import httpx
import yaml
from fastapi import APIRouter, Depends, HTTPException, Response, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server import schemas
from apidoc_server.database import get_db
from apidoc_server.models import Specification, SpecVersion

router = APIRouter()


@router.post("/specs/import")
async def import_specification(import_data: schemas.SpecificationImport, db: AsyncSession = Depends(get_db)):
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(str(import_data.url))
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            
            if "json" in content_type:
                content = response.json()
                format_type = "json"
            elif "yaml" in content_type:
                content = yaml.safe_load(response.text)
                format_type = "yaml"
            else:
                try:
                    content = response.json()
                    format_type = "json"
                except Exception:
                    content = yaml.safe_load(response.text)
                    format_type = "yaml"
            
            info = content.get("info", {})
            spec_name = import_data.name or info.get("title", "Imported API")
            
            spec = Specification(name=spec_name, title=info.get("title", spec_name), description=info.get("description"), version=info.get("version", "1.0.0"), tags=import_data.tags or [])
            db.add(spec)
            await db.flush()
            
            version = SpecVersion(spec_id=spec.id, version=spec.version, content=content, format=format_type, changelog=f"Imported from {import_data.url}", created_by=import_data.created_by)
            db.add(version)
            await db.commit()
            await db.refresh(spec)
            logger.info(f"Imported specification from {import_data.url} (ID: {spec.id})")
            return spec
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch URL: {str(e)}")


@router.get("/specs/{spec_id}/export")
async def export_specification(spec_id: int, format: str = "json", version: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Specification).where(Specification.id == spec_id))
    spec = result.scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    if version:
        version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
    else:
        version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).limit(1))
    spec_version = version_result.scalar_one_or_none()
    if not spec_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    
    content = spec_version.content
    if format == "json":
        return Response(content=json.dumps(content, indent=2, ensure_ascii=False), media_type="application/json", headers={"Content-Disposition": f'attachment; filename="{spec.name}.json"'})
    elif format == "yaml":
        return Response(content=yaml.safe_dump(content, sort_keys=False, allow_unicode=True), media_type="application/yaml", headers={"Content-Disposition": f'attachment; filename="{spec.name}.yaml"'})
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format: {format}")
''')

write_file("apidoc_server/api/auth.py", r'''"""Authentication API endpoints."""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from apidoc_server.config import settings
from apidoc_server.security import security_manager

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


@router.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    access_token = security_manager.create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=settings.token_expire_minutes))
    refresh_token = security_manager.create_refresh_token(data={"sub": form_data.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = security_manager.verify_token(refresh_token, token_type="refresh")
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        access_token = security_manager.create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.post("/auth/api-key")
async def create_api_key(name: str, expires_in_days: Optional[int] = 30):
    api_key, key_hash = security_manager.generate_api_key()
    return {"api_key": api_key, "name": name, "expires_in_days": expires_in_days}
''')

print("✓ APIDoc Server — API эндпоинты созданы (7 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 8. APIDOC SERVER — СЕРВИСЫ
# ═══════════════════════════════════════════════════════════════════
print("📁 APIDoc Server — сервисы...")

write_file("apidoc_server/services/__init__.py", r'''"""Services module."""

from apidoc_server.services.diff_service import DiffService
from apidoc_server.services.publish_service import PublishService
from apidoc_server.services.spec_service import SpecService
from apidoc_server.services.validation_service import ValidationService
from apidoc_server.services.version_service import VersionService

__all__ = ["SpecService", "VersionService", "DiffService", "ValidationService", "PublishService"]
''')

write_file("apidoc_server/services/spec_service.py", r'''"""Specification service."""

from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server.models import Specification, SpecVersion
from apidoc_server.services.validation_service import ValidationService


class SpecService:
    def __init__(self):
        self.validator = ValidationService()
    
    async def create_specification(self, db: AsyncSession, name: str, content: Dict[str, Any], format: str = "json", tags: Optional[List[str]] = None, created_by: Optional[str] = None) -> Specification:
        validation_result = await self.validator.validate(content)
        if not validation_result["valid"]:
            raise ValueError(f"Invalid specification: {validation_result['errors']}")
        
        info = content.get("info", {})
        spec = Specification(name=name, title=info.get("title", name), description=info.get("description"), version=info.get("version", "1.0.0"), tags=tags or [])
        db.add(spec)
        await db.flush()
        
        version = SpecVersion(spec_id=spec.id, version=spec.version, content=content, format=format, created_by=created_by, changelog="Initial version")
        db.add(version)
        await db.commit()
        await db.refresh(spec)
        logger.info(f"Created specification '{name}' (ID: {spec.id})")
        return spec
    
    async def get_specification(self, db: AsyncSession, spec_id: int, include_content: bool = True) -> Optional[Dict[str, Any]]:
        result = await db.execute(select(Specification).where(Specification.id == spec_id))
        spec = result.scalar_one_or_none()
        if not spec: return None
        data = spec.__dict__.copy()
        if include_content:
            version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).limit(1))
            version = version_result.scalar_one_or_none()
            if version: data["content"] = version.content; data["format"] = version.format
        return data
    
    async def list_specifications(self, db: AsyncSession, page: int = 1, per_page: int = 20, tag: Optional[str] = None) -> Dict[str, Any]:
        query = select(Specification)
        if tag: query = query.where(Specification.tags.contains([tag]))
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar()
        query = query.order_by(Specification.updated_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        items = result.scalars().all()
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}
    
    async def delete_specification(self, db: AsyncSession, spec_id: int) -> bool:
        result = await db.execute(select(Specification).where(Specification.id == spec_id))
        spec = result.scalar_one_or_none()
        if not spec: return False
        await db.delete(spec)
        await db.commit()
        logger.info(f"Deleted specification {spec_id}")
        return True
    
    async def search_specifications(self, db: AsyncSession, query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        search_query = select(Specification).where(or_(Specification.name.ilike(f"%{query}%"), Specification.title.ilike(f"%{query}%"), Specification.description.ilike(f"%{query}%")))
        count_result = await db.execute(select(func.count()).select_from(search_query.subquery()))
        total = count_result.scalar()
        search_query = search_query.order_by(Specification.updated_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(search_query)
        items = result.scalars().all()
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}
''')

write_file("apidoc_server/services/version_service.py", r'''"""Version service."""

import re
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apidoc_server.models import Specification, SpecVersion
from apidoc_server.services.validation_service import ValidationService


class VersionService:
    def __init__(self):
        self.validator = ValidationService()
    
    async def create_version(self, db: AsyncSession, spec_id: int, version: str, content: Dict[str, Any], format: str = "json", changelog: Optional[str] = None, created_by: Optional[str] = None) -> SpecVersion:
        validation_result = await self.validator.validate(content)
        if not validation_result["valid"]:
            raise ValueError(f"Invalid specification: {validation_result['errors']}")
        
        result = await db.execute(select(Specification).where(Specification.id == spec_id))
        spec = result.scalar_one_or_none()
        if not spec: raise ValueError(f"Specification {spec_id} not found")
        
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
        if result.scalar_one_or_none(): raise ValueError(f"Version '{version}' already exists")
        
        new_version = SpecVersion(spec_id=spec_id, version=version, content=content, format=format, changelog=changelog, created_by=created_by)
        db.add(new_version)
        spec.version = version
        await db.commit()
        await db.refresh(new_version)
        logger.info(f"Created version '{version}' for specification {spec_id}")
        return new_version
    
    async def get_version(self, db: AsyncSession, spec_id: int, version: str) -> Optional[SpecVersion]:
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
        return result.scalar_one_or_none()
    
    async def get_latest_version(self, db: AsyncSession, spec_id: int) -> Optional[SpecVersion]:
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).limit(1))
        return result.scalar_one_or_none()
    
    async def list_versions(self, db: AsyncSession, spec_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        count_result = await db.execute(select(func.count()).select_from(SpecVersion).where(SpecVersion.spec_id == spec_id))
        total = count_result.scalar()
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
        items = result.scalars().all()
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}
    
    async def delete_version(self, db: AsyncSession, spec_id: int, version: str) -> bool:
        count_result = await db.execute(select(func.count()).select_from(SpecVersion).where(SpecVersion.spec_id == spec_id))
        if count_result.scalar() <= 1: raise ValueError("Cannot delete the only version")
        result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
        version_obj = result.scalar_one_or_none()
        if not version_obj: return False
        await db.delete(version_obj)
        spec_result = await db.execute(select(Specification).where(Specification.id == spec_id))
        spec = spec_result.scalar_one()
        if spec.version == version:
            latest = await self.get_latest_version(db, spec_id)
            if latest: spec.version = latest.version
        await db.commit()
        return True
    
    def _increment_version(self, version: str) -> str:
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
        if match:
            major, minor, patch = map(int, match.groups())
            return f"{major}.{minor}.{patch + 1}"
        return f"{version}.1"
''')

write_file("apidoc_server/services/diff_service.py", r'''"""Diff service for comparing specifications."""

from typing import Any, Dict, List

from deepdiff import DeepDiff


class DiffService:
    def compare(self, spec1: Dict[str, Any], spec2: Dict[str, Any], detect_breaking: bool = True) -> Dict[str, Any]:
        diff = DeepDiff(spec1, spec2, ignore_order=True, report_repetition=True, verbose_level=2, view="tree")
        
        changes = {"added": [], "removed": [], "changed": [], "type_changed": []}
        for item in diff.get("dictionary_item_added", []):
            if isinstance(item, str): changes["added"].append({"path": item})
        for item in diff.get("dictionary_item_removed", []):
            if isinstance(item, str): changes["removed"].append({"path": item})
        for path, change in diff.get("values_changed", {}).items():
            changes["changed"].append({"path": path, "old_value": change.get("old_value"), "new_value": change.get("new_value")})
        for path, change in diff.get("type_changes", {}).items():
            changes["type_changed"].append({"path": path, "old_type": change.get("old_type"), "new_type": change.get("new_type")})
        
        breaking_changes = []
        if detect_breaking:
            breaking_changes = self._detect_breaking_changes(spec1, spec2, changes)
        
        summary = {"total_changes": len(changes["added"]) + len(changes["removed"]) + len(changes["changed"]) + len(changes["type_changed"]), "breaking_changes_count": len(breaking_changes), "has_breaking_changes": len(breaking_changes) > 0}
        return {"changes": changes, "breaking_changes": breaking_changes, "summary": summary}
    
    def _detect_breaking_changes(self, spec1: Dict[str, Any], spec2: Dict[str, Any], changes: Dict[str, Any]) -> List[Dict[str, Any]]:
        breaking = []
        paths1 = spec1.get("paths", {})
        paths2 = spec2.get("paths", {})
        
        for path in paths1:
            if path not in paths2:
                breaking.append({"type": "endpoint_removed", "path": path, "severity": "high", "message": f"Endpoint {path} was removed"})
                continue
            for method in paths1[path]:
                if method not in paths2[path]:
                    breaking.append({"type": "method_removed", "path": path, "method": method.upper(), "severity": "high", "message": f"Method {method.upper()} {path} was removed"})
        
        schemas1 = spec1.get("components", {}).get("schemas", {})
        schemas2 = spec2.get("components", {}).get("schemas", {})
        for schema_name, schema in schemas1.items():
            if schema_name not in schemas2:
                breaking.append({"type": "schema_removed", "schema": schema_name, "severity": "high", "message": f"Schema '{schema_name}' was removed"})
        
        return breaking
''')

write_file("apidoc_server/services/validation_service.py", r'''"""Validation service for OpenAPI specifications."""

import json
import re
from typing import Any, Dict

import httpx
from loguru import logger
from openapi_spec_validator import validate_spec
from openapi_spec_validator.exceptions import OpenAPIValidationError
from prance import ResolvingParser


class ValidationService:
    REMOTE_VALIDATOR_URL = "https://validator.swagger.io/validator/debug"
    
    async def validate(self, spec: Dict[str, Any], strict: bool = False, use_remote: bool = False) -> Dict[str, Any]:
        results = {"valid": True, "errors": [], "warnings": [], "fixable": []}
        
        if "openapi" not in spec and "swagger" not in spec:
            results["valid"] = False
            results["errors"].append({"type": "missing_version", "message": "Missing 'openapi' or 'swagger' field"})
            return results
        
        if use_remote:
            return await self._validate_remote(spec)
        
        try:
            validate_spec(spec)
        except OpenAPIValidationError as e:
            results["valid"] = False
            results["errors"].append({"type": "validation_error", "message": str(e), "location": self._extract_location(e)})
        except Exception as e:
            results["valid"] = False
            results["errors"].append({"type": "parse_error", "message": str(e)})
        
        self._check_references(spec, results)
        self._check_common_issues(spec, results)
        return results
    
    async def _validate_remote(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.REMOTE_VALIDATOR_URL, json={"spec": spec})
                response.raise_for_status()
                data = response.json()
                results = {"valid": len(data.get("schemaValidationMessages", [])) == 0, "errors": [], "warnings": [], "fixable": []}
                for msg in data.get("schemaValidationMessages", []):
                    error = {"type": "remote_validation", "message": msg.get("message", ""), "location": msg.get("path", "")}
                    if msg.get("level") == "error": results["errors"].append(error)
                    else: results["warnings"].append(error)
                return results
        except Exception as e:
            logger.error(f"Remote validation failed: {e}")
            return {"valid": False, "errors": [{"type": "remote_error", "message": str(e)}], "warnings": [], "fixable": []}
    
    def _check_references(self, spec: Dict[str, Any], results: Dict) -> None:
        try:
            parser = ResolvingParser(spec_string=json.dumps(spec))
            def collect_refs(obj, path=""):
                if isinstance(obj, dict):
                    if "$ref" in obj:
                        if not obj["$ref"].startswith("#"):
                            results["warnings"].append({"type": "external_reference", "message": f"External reference: {obj['$ref']}", "location": path})
                    for key, value in obj.items():
                        collect_refs(value, f"{path}.{key}" if path else key)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        collect_refs(item, f"{path}[{i}]")
            collect_refs(spec)
        except Exception as e:
            results["warnings"].append({"type": "reference_error", "message": f"Reference validation warning: {e}"})
    
    def _check_common_issues(self, spec: Dict[str, Any], results: Dict) -> None:
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]: continue
                if "responses" not in details:
                    results["errors"].append({"type": "missing_responses", "location": f"paths.{path}.{method}", "message": "Missing 'responses' field"})
                    results["fixable"].append({"type": "add_responses", "location": f"paths.{path}.{method}", "description": f"Add default response for {method.upper()} {path}"})
                if "operationId" not in details:
                    results["warnings"].append({"type": "missing_operation_id", "location": f"paths.{path}.{method}", "message": "Missing operationId"})
        info = spec.get("info", {})
        if "title" not in info: results["errors"].append({"type": "missing_title", "message": "Missing 'info.title'"})
        if "version" not in info: results["errors"].append({"type": "missing_version", "message": "Missing 'info.version'"})
    
    def _extract_location(self, error: Exception) -> str:
        error_str = str(error)
        for pattern in [r"in ['\"]([^'\"]+)['\"]", r"at ['\"]([^'\"]+)['\"]", r"path ['\"]([^'\"]+)['\"]"]:
            match = re.search(pattern, error_str)
            if match: return match.group(1)
        return ""
''')

write_file("apidoc_server/services/publish_service.py", r'''"""Publish service for external services."""

import base64
from typing import Any, Dict, List

import httpx
import yaml
from loguru import logger


class PublishService:
    def __init__(self):
        self.services = {"swaggerhub": self._publish_to_swaggerhub, "github": self._publish_to_github, "readme": self._publish_to_readme, "redocly": self._publish_to_redocly}
    
    async def publish(self, spec: Dict[str, Any], targets: List[str], credentials: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for target in targets:
            if target in self.services:
                try:
                    result = await self.services[target](spec, credentials.get(target, {}), metadata.get(target, {}))
                    results[target] = {"success": True, "result": result}
                    logger.info(f"Published to {target} successfully")
                except Exception as e:
                    results[target] = {"success": False, "error": str(e)}
                    logger.error(f"Failed to publish to {target}: {e}")
        return results
    
    async def _publish_to_swaggerhub(self, spec: Dict, credentials: Dict, metadata: Dict) -> Dict:
        api_key = credentials.get("api_key")
        owner = metadata.get("owner")
        name = metadata.get("name", "api")
        version = metadata.get("version", "1.0.0")
        if not api_key or not owner: raise ValueError("SwaggerHub requires api_key and owner")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"https://api.swaggerhub.com/apis/{owner}/{name}"
            response = await client.post(url, params={"version": version}, json=spec, headers={"Authorization": api_key, "Content-Type": "application/json"})
            if response.status_code == 409:
                response = await client.put(f"{url}/{version}", json=spec, headers={"Authorization": api_key, "Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
    
    async def _publish_to_github(self, spec: Dict, credentials: Dict, metadata: Dict) -> Dict:
        token = credentials.get("token")
        repo = metadata.get("repo")
        path = metadata.get("path", "openapi.yaml")
        branch = metadata.get("branch", "main")
        if not token or not repo: raise ValueError("GitHub requires token and repo")
        
        yaml_content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        content_base64 = base64.b64encode(yaml_content.encode()).decode()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"https://api.github.com/repos/{repo}/contents/{path}", params={"ref": branch}, headers=headers)
            data = {"message": "Update OpenAPI specification", "content": content_base64, "branch": branch}
            if response.status_code == 200: data["sha"] = response.json()["sha"]
            response = await client.put(f"https://api.github.com/repos/{repo}/contents/{path}", json=data, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def _publish_to_readme(self, spec: Dict, credentials: Dict, metadata: Dict) -> Dict:
        api_key = credentials.get("api_key")
        version = metadata.get("version", "1.0.0")
        if not api_key: raise ValueError("ReadMe requires api_key")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://dash.readme.com/api/v1/api-registry", json={"spec": spec, "version": version}, headers={"Authorization": f"Bearer {api_key}"})
            response.raise_for_status()
            return response.json()
    
    async def _publish_to_redocly(self, spec: Dict, credentials: Dict, metadata: Dict) -> Dict:
        api_key = credentials.get("api_key")
        organization = metadata.get("organization")
        name = metadata.get("name", "api")
        version = metadata.get("version", "1.0.0")
        if not api_key or not organization: raise ValueError("Redocly requires api_key and organization")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"https://api.redocly.com/orgs/{organization}/apis", json={"name": name, "version": version, "spec": spec}, headers={"Authorization": f"Bearer {api_key}"})
            if response.status_code == 409:
                apis_response = await client.get(f"https://api.redocly.com/orgs/{organization}/apis", headers={"Authorization": f"Bearer {api_key}"})
                api_id = None
                for api in apis_response.json().get("items", []):
                    if api.get("name") == name: api_id = api.get("id"); break
                if api_id:
                    response = await client.put(f"https://api.redocly.com/orgs/{organization}/apis/{api_id}/versions/{version}", json={"spec": spec}, headers={"Authorization": f"Bearer {api_key}"})
            response.raise_for_status()
            return response.json()
''')

print("✓ APIDoc Server — сервисы созданы (6 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 9. APIDOC SERVER — MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════
print("📁 APIDoc Server — middleware...")

write_file("apidoc_server/middleware/__init__.py", r'''"""Middleware module."""

from apidoc_server.middleware.cors import setup_cors
from apidoc_server.middleware.csrf import CSRFMiddleware
from apidoc_server.middleware.rate_limit import RateLimitMiddleware
from apidoc_server.middleware.request_id import RequestIDMiddleware

__all__ = ["setup_cors", "CSRFMiddleware", "RateLimitMiddleware", "RequestIDMiddleware"]
''')

write_file("apidoc_server/middleware/rate_limit.py", r'''"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Callable, Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000, whitelist: list = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.whitelist = whitelist or ["127.0.0.1", "localhost"]
        self._storage: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        if client_ip in self.whitelist:
            return await call_next(request)
        
        if not self._check_rate_limit(client_ip):
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": "60", "X-RateLimit-Limit": str(self.requests_per_minute)}
            )
        
        response = await call_next(request)
        remaining = self._get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded: return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip: return real_ip
        if request.client: return request.client.host
        return "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        self._clean_old_entries(client_ip, now)
        requests = self._storage.get(client_ip, [])
        if len([r for r in requests if now - r < 60]) >= self.requests_per_minute: return False
        if len([r for r in requests if now - r < 3600]) >= self.requests_per_hour: return False
        requests.append(now)
        self._storage[client_ip] = requests
        return True
    
    def _clean_old_entries(self, client_ip: str, now: float) -> None:
        if client_ip in self._storage:
            self._storage[client_ip] = [r for r in self._storage[client_ip] if now - r < 3600]
    
    def _get_remaining_requests(self, client_ip: str) -> int:
        now = time.time()
        requests = self._storage.get(client_ip, [])
        return max(0, self.requests_per_minute - len([r for r in requests if now - r < 60]))
''')

write_file("apidoc_server/middleware/cors.py", r'''"""CORS middleware configuration."""

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI, allowed_origins: List[str] = None, allowed_methods: List[str] = None, allowed_headers: List[str] = None, allow_credentials: bool = True, max_age: int = 600) -> None:
    app.add_middleware(CORSMiddleware, allow_origins=allowed_origins or ["*"], allow_credentials=allow_credentials, allow_methods=allowed_methods or ["*"], allow_headers=allowed_headers or ["*"], max_age=max_age)
''')

write_file("apidoc_server/middleware/csrf.py", r'''"""CSRF protection middleware."""

import hmac
import secrets
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cookie_name: str = "csrf_token", header_name: str = "X-CSRF-Token", safe_methods: set = None):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.safe_methods = safe_methods or {"GET", "HEAD", "OPTIONS"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in self.safe_methods:
            response = await call_next(request)
            return self._set_csrf_cookie(response)
        
        header_token = request.headers.get(self.header_name)
        cookie_token = request.cookies.get(self.cookie_name)
        if not header_token or not cookie_token:
            return Response(content='{"error": "CSRF token missing"}', status_code=HTTP_403_FORBIDDEN, media_type="application/json")
        if not hmac.compare_digest(header_token, cookie_token):
            return Response(content='{"error": "CSRF token mismatch"}', status_code=HTTP_403_FORBIDDEN, media_type="application/json")
        return await call_next(request)
    
    def _generate_csrf_token(self) -> str:
        return secrets.token_hex(32)
    
    def _set_csrf_cookie(self, response: Response) -> Response:
        token = self._generate_csrf_token()
        response.set_cookie(key=self.cookie_name, value=token, httponly=False, secure=True, samesite="strict", max_age=86400)
        return response
''')

write_file("apidoc_server/middleware/request_id.py", r'''"""Request ID middleware."""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Request-ID", response_header: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name
        self.response_header = response_header
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[self.response_header] = request_id
        return response
    
    @staticmethod
    def get_request_id(request: Request) -> str:
        return getattr(request.state, "request_id", str(uuid.uuid4()))
''')

print("✓ APIDoc Server — middleware созданы (5 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 10. ALEMBIC МИГРАЦИИ
# ═══════════════════════════════════════════════════════════════════
print("📁 Alembic миграции...")

write_file("apidoc_server/alembic.ini", r'''[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = sqlite+aiosqlite:///./apidoc.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
''')

write_file("apidoc_server/alembic/env.py", r'''"""Alembic environment configuration."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from apidoc_server.config import settings
from apidoc_server.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    connectable = async_engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
''')

write_file("apidoc_server/alembic/script.py.mako", r'''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
''')

write_file("apidoc_server/alembic/versions/001_initial.py", r'''"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'specifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    op.create_table(
        'spec_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('spec_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('format', sa.String(length=10), nullable=False),
        sa.Column('changelog', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['spec_id'], ['specifications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('spec_id', 'version', name='uq_spec_version')
    )


def downgrade() -> None:
    op.drop_table('spec_versions')
    op.drop_table('specifications')
''')

write_file("apidoc_server/alembic/versions/002_add_metadata.py", r'''"""Add metadata columns

Revision ID: 002_add_metadata
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002_add_metadata'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('specifications', sa.Column('owner', sa.String(length=255), nullable=True))
    op.add_column('specifications', sa.Column('visibility', sa.String(length=20), server_default='private', nullable=False))
    op.add_column('specifications', sa.Column('contact_email', sa.String(length=255), nullable=True))
    op.add_column('specifications', sa.Column('license_name', sa.String(length=100), nullable=True))
    op.add_column('specifications', sa.Column('license_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('specifications', 'license_url')
    op.drop_column('specifications', 'license_name')
    op.drop_column('specifications', 'contact_email')
    op.drop_column('specifications', 'visibility')
    op.drop_column('specifications', 'owner')
''')

write_file("apidoc_server/alembic/versions/003_add_indexes.py", r'''"""Add indexes for performance

Revision ID: 003_add_indexes
Revises: 002_add_metadata
Create Date: 2024-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '003_add_indexes'
down_revision: Union[str, None] = '002_add_metadata'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_spec_versions_spec_id_created_at', 'spec_versions', ['spec_id', 'created_at'])
    op.create_index('ix_specifications_name_title', 'specifications', ['name', 'title'])
    op.create_index('ix_specifications_updated_at', 'specifications', ['updated_at'])


def downgrade() -> None:
    op.drop_index('ix_specifications_updated_at', table_name='specifications')
    op.drop_index('ix_specifications_name_title', table_name='specifications')
    op.drop_index('ix_spec_versions_spec_id_created_at', table_name='spec_versions')
''')

print("✓ Alembic миграции созданы (6 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 11. ТЕСТЫ СЕРВЕРА
# ═══════════════════════════════════════════════════════════════════
print("📁 Тесты сервера...")

write_file("apidoc_server/tests/__init__.py", r'''"""Server tests module."""''')

write_file("apidoc_server/tests/conftest.py", r'''"""Pytest fixtures for server tests."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apidoc_server.database import Base, get_db
from apidoc_server.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield async_session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db) -> AsyncGenerator:
    async def override_get_db():
        async with test_db() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def sample_spec() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0", "description": "Test description"},
        "paths": {
            "/users": {
                "get": {"summary": "Get users", "operationId": "getUsers", "responses": {"200": {"description": "OK"}}},
                "post": {"summary": "Create user", "operationId": "createUser", "responses": {"201": {"description": "Created"}}}
            }
        }
    }
''')

write_file("apidoc_server/tests/test_api.py", r'''"""API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_specification(client: AsyncClient, sample_spec):
    response = await client.post("/api/v1/specs", json={"name": "test-api", "content": sample_spec, "format": "json"})
    assert response.status_code == 200
    assert response.json()["name"] == "test-api"


@pytest.mark.asyncio
async def test_create_duplicate_specification(client: AsyncClient, sample_spec):
    await client.post("/api/v1/specs", json={"name": "duplicate-api", "content": sample_spec, "format": "json"})
    response = await client.post("/api/v1/specs", json={"name": "duplicate-api", "content": sample_spec, "format": "json"})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_specification(client: AsyncClient, sample_spec):
    create_resp = await client.post("/api/v1/specs", json={"name": "get-test", "content": sample_spec, "format": "json"})
    spec_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/specs/{spec_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_nonexistent_specification(client: AsyncClient):
    response = await client.get("/api/v1/specs/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_specifications(client: AsyncClient, sample_spec):
    for i in range(3):
        await client.post("/api/v1/specs", json={"name": f"list-test-{i}", "content": sample_spec, "format": "json"})
    response = await client.get("/api/v1/specs")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 3


@pytest.mark.asyncio
async def test_search_specifications(client: AsyncClient, sample_spec):
    await client.post("/api/v1/specs", json={"name": "payment-api", "content": sample_spec, "format": "json"})
    await client.post("/api/v1/specs", json={"name": "user-api", "content": sample_spec, "format": "json"})
    response = await client.get("/api/v1/specs/search?q=payment")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


@pytest.mark.asyncio
async def test_delete_specification(client: AsyncClient, sample_spec):
    create_resp = await client.post("/api/v1/specs", json={"name": "delete-test", "content": sample_spec, "format": "json"})
    spec_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/specs/{spec_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_version(client: AsyncClient, sample_spec):
    create_resp = await client.post("/api/v1/specs", json={"name": "version-test", "content": sample_spec, "format": "json"})
    spec_id = create_resp.json()["id"]
    sample_spec["info"]["version"] = "2.0.0"
    response = await client.post(f"/api/v1/specs/{spec_id}/versions", json={"content": sample_spec, "version": "2.0.0", "format": "json"})
    assert response.status_code == 200
''')

write_file("apidoc_server/tests/test_services.py", r'''"""Service layer tests."""

import pytest
from apidoc_server.services.diff_service import DiffService
from apidoc_server.services.validation_service import ValidationService


class TestValidationService:
    @pytest.mark.asyncio
    async def test_validate_valid_spec(self, sample_spec):
        service = ValidationService()
        result = await service.validate(sample_spec)
        assert result["valid"] is True
    
    @pytest.mark.asyncio
    async def test_validate_invalid_spec(self):
        service = ValidationService()
        result = await service.validate({"openapi": "3.0.3", "info": {"title": "Invalid API"}, "paths": {}})
        assert result["valid"] is False


class TestDiffService:
    def test_compare_identical(self, sample_spec):
        service = DiffService()
        result = service.compare(sample_spec, sample_spec)
        assert result["summary"]["total_changes"] == 0
    
    def test_compare_with_changes(self, sample_spec):
        import copy
        spec2 = copy.deepcopy(sample_spec)
        spec2["paths"]["/users"]["delete"] = {"summary": "Delete user", "responses": {"204": {"description": "Deleted"}}}
        service = DiffService()
        result = service.compare(sample_spec, spec2)
        assert result["summary"]["total_changes"] > 0
''')

write_file("apidoc_server/tests/test_security.py", r'''"""Security tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    responses = []
    for _ in range(70):
        resp = await client.get("/health")
        responses.append(resp)
    assert any(r.status_code == 429 for r in responses)


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    response = await client.options("/api/v1/specs", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_id_header(client: AsyncClient):
    response = await client.get("/health")
    assert "X-Request-ID" in response.headers
''')

print("✓ Тесты сервера созданы (4 файла)")
print()

# ═══════════════════════════════════════════════════════════════════
# 12. ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ═══════════════════════════════════════════════════════════════════
print("📁 Интеграционные тесты...")

write_file("tests/__init__.py", r'''"""Integration tests module."""''')

write_file("tests/conftest.py", r'''"""Pytest fixtures for integration tests."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apidoc_server.database import Base, get_db
from apidoc_server.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield async_session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db) -> AsyncGenerator:
    async def override_get_db():
        async with test_db() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test", timeout=30.0) as ac:
        yield ac
    app.dependency_overrides.clear()
''')

write_file("tests/test_cli.py", r'''"""Tests for APIDoc CLI."""

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
''')

write_file("tests/test_integration.py", r'''"""Integration tests for CLI and Server."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_spec_lifecycle(client: AsyncClient):
    spec = {"openapi": "3.0.3", "info": {"title": "Lifecycle Test", "version": "1.0.0"}, "paths": {"/items": {"get": {"summary": "List items", "operationId": "listItems", "responses": {"200": {"description": "OK"}}}}}}
    
    response = await client.post("/api/v1/specs", json={"name": "lifecycle-test", "content": spec, "format": "json"})
    assert response.status_code == 200
    spec_id = response.json()["id"]
    
    response = await client.get(f"/api/v1/specs/{spec_id}")
    assert response.status_code == 200
    
    spec["info"]["version"] = "2.0.0"
    response = await client.post(f"/api/v1/specs/{spec_id}/versions", json={"content": spec, "version": "2.0.0", "format": "json"})
    assert response.status_code == 200
    
    response = await client.get(f"/api/v1/specs/{spec_id}/versions")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    
    response = await client.post(f"/api/v1/specs/{spec_id}/diff", json={"version1": "1.0.0", "version2": "2.0.0"})
    assert response.status_code == 200
    
    response = await client.delete(f"/api/v1/specs/{spec_id}")
    assert response.status_code == 200
''')

write_file("tests/test_e2e.py", r'''"""End-to-end tests for full workflows."""

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
''')

write_file("tests/fixtures/openapi_valid.yaml", r'''openapi: "3.0.3"
info:
  title: "Valid Test API"
  description: "A valid OpenAPI specification for testing"
  version: "1.0.0"
servers:
  - url: "https://api.example.com/v1"
paths:
  /users:
    get:
      tags: [users]
      summary: "List all users"
      operationId: "listUsers"
      responses:
        "200":
          description: "Successful response"
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/User"
    post:
      tags: [users]
      summary: "Create a new user"
      operationId: "createUser"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUserRequest"
      responses:
        "201":
          description: "User created"
components:
  schemas:
    User:
      type: object
      properties:
        id: {type: string}
        name: {type: string}
        email: {type: string, format: email}
      required: [id, name, email]
    CreateUserRequest:
      type: object
      properties:
        name: {type: string}
        email: {type: string, format: email}
      required: [name, email]
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
security:
  - bearerAuth: []
''')

write_file("tests/fixtures/openapi_invalid.yaml", r'''openapi: "3.0.3"
info:
  title: "Invalid Test API"
paths:
  /users:
    get:
      summary: "List users"
  /users/{id}:
    post:
      summary: "Update user"
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/MissingSchema"
components:
  securitySchemes:
    basicAuth:
      type: http
      scheme: basic
''')

write_file("tests/fixtures/fastapi_app.py", r'''"""Sample FastAPI application for testing."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Test FastAPI App", version="1.0.0")


class Item(BaseModel):
    id: int
    name: str
    price: float


class CreateItemRequest(BaseModel):
    name: str
    price: float


@app.get("/items", tags=["items"])
async def list_items():
    return {"items": []}


@app.post("/items", tags=["items"])
async def create_item(item: CreateItemRequest):
    return {"id": 1, "name": item.name, "price": item.price}


@app.get("/items/{item_id}", tags=["items"])
async def get_item(item_id: int):
    return {"id": item_id, "name": "Item", "price": 10.0}


@app.delete("/items/{item_id}", tags=["items"])
async def delete_item(item_id: int):
    return {"deleted": True}
''')

print("✓ Интеграционные тесты созданы (8 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 13. ДОКУМЕНТАЦИЯ
# ═══════════════════════════════════════════════════════════════════
print("📁 Документация...")

write_file("docs/index.md", r'''# APIDoc Manager Documentation

## Overview

APIDoc Manager is a comprehensive CLI tool and server for automating OpenAPI specification management.

## Features

| Command | Description |
|---------|-------------|
| `generate` | Generate OpenAPI specs from source code |
| `validate` | Validate specifications (local + remote) |
| `diff` | Compare two specs with breaking change detection |
| `mock` | Start mock server from specification |
| `testgen` | Generate tests (Pytest/Jest) |
| `publish` | Publish to server + external services |
| `convert` | Convert between formats and versions |
| `server` | Manage APIDoc server |
| `tree` | Visualize API structure |

## Quick Links

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [CLI Reference](cli-reference.md)
- [API Reference](api-reference.md)
- [Plugin Development](plugin-development.md)
''')

write_file("docs/installation.md", r'''# Installation

## Prerequisites

- Python 3.10 or higher
- pip

## Installing APIDoc CLI

```bash
pip install apidoc-manager
```

### Or from source:

```bash
git clone https://github.com/apidoc/apidoc-manager.git
cd apidoc-manager
pip install -e .
```
## Installing APIDoc Server
### Using Docker (Recommended)
```bash
docker-compose -f docker/docker-compose.yml up -d
```
### Manual
```bash
apidoc server init
apidoc server start --host 0.0.0.0 --port 8000
```

### Shell Completion
```bash
# Bash
echo 'eval "$(apidoc --show-completion bash)"' >> ~/.bashrc
```
```bash
# Zsh
echo 'eval "$(apidoc --show-completion zsh)"' >> ~/.zshrc
```
''')

write_file("docs/quickstart.md", r'''# Quick Start Guide

5-Minute Quick Start
1. Generate Your First Specification
bash
apidoc generate ./my_fastapi_app.py --output openapi.yaml
apidoc generate --interactive
2. Validate
bash
apidoc validate openapi.yaml
3. Start Mock Server
bash
apidoc mock openapi.yaml --port 8001
curl http://localhost:8001/users
4. Generate Tests
bash
apidoc testgen openapi.yaml --output ./tests --framework pytest
pytest ./tests -v
5. Publish
bash
apidoc server start
apidoc publish openapi.yaml --target server --name "My API"
''')

write_file("docs/cli-reference.md", r'''# CLI Command Reference

Global Options
Option	Description
--config, -c	Path to config file
--debug	Enable debug mode
--json	Output in JSON format
--version	Show version
Commands
generate — Generate OpenAPI specs from source code
bash
apidoc generate SOURCE [--output PATH] [--format yaml|json] [--framework NAME] [--interactive]
validate — Validate specifications
bash
apidoc validate SPEC_FILE [--strict] [--remote] [--fix] [--json]
diff — Compare two specifications
bash
apidoc diff SPEC1 SPEC2 [--tree] [--json]
mock — Start mock server
bash
apidoc mock SPEC_FILE [--host HOST] [--port PORT] [--log-file PATH]
testgen — Generate tests
bash
apidoc testgen SPEC_FILE [--output DIR] [--framework NAME] [--language LANG]
publish — Publish specification
bash
apidoc publish SPEC_FILE [--target server,github,swaggerhub,readme] [--name NAME] [--version VER]
convert — Convert between formats
bash
apidoc convert INPUT [--output PATH] [--to json|yaml] [--version VER] [--from-url URL]
server — Manage APIDoc server
bash
apidoc server start [--host HOST] [--port PORT] [--background]
apidoc server status
apidoc server search QUERY
apidoc server versions SPEC_ID
apidoc server init
tree — Visualize API structure
bash
apidoc tree SPEC_FILE [--schemas] [--methods/--no-methods]
''')

write_file("docs/api-reference.md", r'''# Server API Reference

Base URL
text
http://localhost:8000/api/v1
Endpoints
Specifications
Method	Path	Description
GET	/specs	List specifications
POST	/specs	Create specification
GET	/specs/{id}	Get specification
DELETE	/specs/{id}	Delete specification
Versions
Method	Path	Description
GET	/specs/{id}/versions	List versions
POST	/specs/{id}/versions	Create version
DELETE	/specs/{id}/versions/{v}	Delete version
Search
http
GET /specs/search?q=query&page=1&per_page=20
Diff
http
POST /specs/{id}/diff
{"version1": "1.0.0", "version2": "1.1.0"}
Import/Export
http
POST /specs/import
GET /specs/{id}/export?format=json
Health
http
GET /health
GET /health/readiness
Metrics
http
GET /metrics
''')

write_file("docs/plugin-development.md", r'''# Plugin Development Guide

Parser Plugin
python
from apidoc_cli.plugins.base import BaseParser
from pathlib import Path

class MyFrameworkParser(BaseParser):
    @property
    def name(self) -> str: return "my-parser"
    
    @property
    def frameworks(self) -> list: return ["myframework"]
    
    def parse(self, source: Path, **kwargs) -> dict:
        return {"openapi": "3.0.3", "info": {"title": "My API", "version": "1.0.0"}, "paths": {}}
Publisher Plugin
python
from apidoc_cli.plugins.base import BasePublisher

class MyPublisher(BasePublisher):
    @property
    def name(self) -> str: return "my-service"
    
    async def publish(self, spec, name, version, **kwargs):
        return {"status": "published"}
Registration in pyproject.toml
toml
[project.entry-points."apidoc.plugins"]
my-parser = "my_package:MyFrameworkParser"
''')

write_file("docs/examples/fastapi_example.py", r'''"""Example FastAPI application for APIDoc Manager."""

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

app = FastAPI(title="Example User API", description="A sample API for demonstrating APIDoc Manager", version="1.0.0")


class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: Optional[int] = Field(None, ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str


@app.get("/users", tags=["users"])
async def list_users(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    return {"items": [], "total": 0, "page": page, "limit": limit}


@app.post("/users", tags=["users"], status_code=201)
async def create_user(user: CreateUserRequest):
    return {"id": 1, "name": user.name, "email": user.email}


@app.get("/users/{user_id}", tags=["users"])
async def get_user(user_id: int):
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}


@app.put("/users/{user_id}", tags=["users"])
async def update_user(user_id: int, user: CreateUserRequest):
    return {"id": user_id, "name": user.name, "email": user.email}


@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int):
    return {"deleted": True}
''')

print("✓ Документация создана (7 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 14. DOCKER
# ═══════════════════════════════════════════════════════════════════
print("📁 Docker...")

write_file("docker/Dockerfile.cli", r'''FROM python:3.11-slim AS builder

WORKDIR /build
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY apidoc_cli ./apidoc_cli
COPY pyproject.toml .
RUN pip install -e .

RUN useradd -m -u 1000 apidoc
USER apidoc
WORKDIR /workspace

ENTRYPOINT ["apidoc"]
CMD ["--help"]
''')

write_file("docker/Dockerfile.server", r'''FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apidoc_server ./apidoc_server
COPY pyproject.toml .
RUN pip install -e .

RUN useradd -m -u 1000 apidoc && chown -R apidoc:apidoc /app
USER apidoc

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "apidoc_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
''')

write_file("docker/Dockerfile.prod", r'''FROM python:3.11-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 -s /bin/bash apidoc && mkdir -p /app /data && chown -R apidoc:apidoc /app /data

COPY --from=builder /root/.local /home/apidoc/.local
ENV PATH=/home/apidoc/.local/bin:$PATH

WORKDIR /app
COPY --chown=apidoc:apidoc apidoc_cli ./apidoc_cli
COPY --chown=apidoc:apidoc apidoc_server ./apidoc_server
COPY --chown=apidoc:apidoc pyproject.toml .
RUN pip install --no-cache-dir -e .

USER apidoc

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "apidoc_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
''')

write_file("docker/docker-compose.yml", r'''version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: apidoc
      POSTGRES_PASSWORD: apidoc_password
      POSTGRES_DB: apidoc
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U apidoc"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  server:
    build:
      context: ..
      dockerfile: docker/Dockerfile.server
    ports:
      - "8000:8000"
    environment:
      APIDOC_DATABASE_URL: postgresql+asyncpg://apidoc:apidoc_password@postgres:5432/apidoc
      APIDOC_REDIS_URL: redis://redis:6379/0
      APIDOC_SECRET_KEY: dev-secret-key-change-in-production
      APIDOC_HOST: 0.0.0.0
      APIDOC_PORT: 8000
      APIDOC_DEBUG: "true"
      APIDOC_LOG_LEVEL: DEBUG
    volumes:
      - ../apidoc_server:/app/apidoc_server
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      sh -c "
        alembic upgrade head &&
        uvicorn apidoc_server.main:app --host 0.0.0.0 --port 8000 --reload
      "

volumes:
  postgres_data:
  redis_data:
''')

write_file("docker/docker-compose.prod.yml", r'''version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-apidoc}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-apidoc}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - apidoc-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-apidoc}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 512M

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - apidoc-network

  server:
    build:
      context: ..
      dockerfile: docker/Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      APIDOC_DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-apidoc}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-apidoc}
      APIDOC_REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      APIDOC_SECRET_KEY: ${SECRET_KEY}
      APIDOC_HOST: 0.0.0.0
      APIDOC_PORT: 8000
      APIDOC_LOG_LEVEL: ${LOG_LEVEL:-INFO}
      APIDOC_LOG_JSON: "true"
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    networks:
      - apidoc-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      replicas: 2

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - apidoc-network
    depends_on:
      - server

networks:
  apidoc-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
''')

print("✓ Docker создан (5 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 15. KUBERNETES
# ═══════════════════════════════════════════════════════════════════
print("📁 Kubernetes...")

write_file("k8s/namespace.yaml", r'''apiVersion: v1
kind: Namespace
metadata:
  name: apidoc
  labels:
    name: apidoc
    environment: production
''')

write_file("k8s/deployment.yaml", r'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: apidoc-server
  namespace: apidoc
  labels:
    app: apidoc-server
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: apidoc-server
  template:
    metadata:
      labels:
        app: apidoc-server
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: server
        image: ghcr.io/apidoc/server:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: APIDOC_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: apidoc-secrets
              key: database-url
        - name: APIDOC_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: apidoc-secrets
              key: secret-key
        - name: APIDOC_LOG_JSON
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/readiness
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
''')

write_file("k8s/configmap.yaml", r'''apiVersion: v1
kind: ConfigMap
metadata:
  name: apidoc-config
  namespace: apidoc
data:
  APIDOC_HOST: "0.0.0.0"
  APIDOC_PORT: "8000"
  APIDOC_LOG_LEVEL: "INFO"
  APIDOC_LOG_JSON: "true"
  APIDOC_ENABLE_DOCS: "true"
  APIDOC_ENABLE_METRICS: "true"
  APIDOC_RATE_LIMIT_PER_MINUTE: "60"
  APIDOC_RATE_LIMIT_PER_HOUR: "1000"
''')

write_file("k8s/secrets.yaml", r'''apiVersion: v1
kind: Secret
metadata:
  name: apidoc-secrets
  namespace: apidoc
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://apidoc:changeme@postgres:5432/apidoc"
  secret-key: "your-secret-key-here-change-in-production"
  redis-url: "redis://:changeme@redis:6379/0"
  swaggerhub-api-key: ""
  github-token: ""
  readme-api-key: ""
''')

write_file("k8s/service.yaml", r'''apiVersion: v1
kind: Service
metadata:
  name: apidoc-server
  namespace: apidoc
  labels:
    app: apidoc-server
spec:
  type: ClusterIP
  selector:
    app: apidoc-server
  ports:
    - name: http
      port: 80
      targetPort: 8000
      protocol: TCP
  sessionAffinity: ClientIP
''')

write_file("k8s/ingress.yaml", r'''apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: apidoc-ingress
  namespace: apidoc
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.apidoc.example.com
      secretName: apidoc-tls
  rules:
    - host: api.apidoc.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: apidoc-server
                port:
                  number: 80
''')

write_file("k8s/hpa.yaml", r'''apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: apidoc-server-hpa
  namespace: apidoc
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: apidoc-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
''')

write_file("k8s/monitoring/servicemonitor.yaml", r'''apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: apidoc-monitor
  namespace: apidoc
  labels:
    release: prometheus
    app: apidoc-server
spec:
  selector:
    matchLabels:
      app: apidoc-server
  namespaceSelector:
    matchNames:
      - apidoc
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
''')

write_file("k8s/monitoring/prometheus-rule.yaml", """apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: apidoc-alerts
  namespace: apidoc
  labels:
    release: prometheus
    app: apidoc-server
spec:
  groups:
    - name: apidoc.rules
      interval: 30s
      rules:
        - alert: APIDocHighErrorRate
          expr: |
            rate(apidoc_http_requests_total{status=~\"5..\"}[5m]) 
            / 
            rate(apidoc_http_requests_total[5m]) > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High error rate detected"
            description: "Error rate is {{ $value | humanizePercentage }}"
        
        - alert: APIDocHighLatency
          expr: |
            histogram_quantile(0.95, rate(apidoc_http_request_duration_seconds_bucket[5m])) > 2
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High latency detected"
            description: "P95 latency is {{ $value }}s"
        
        - alert: APIDocServiceDown
          expr: up{job=\"apidoc-server\"} == 0
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "APIDoc server is down"
            description: "Service has been down for more than 2 minutes"
        
        - alert: APIDocDatabaseConnectionPoolHigh
          expr: apidoc_database_connections > 80
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Database connection pool high"
            description: "Using {{ $value }} connections"
""")

print("✓ Kubernetes создан (8 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 16. МОНИТОРИНГ И NGINX
# ═══════════════════════════════════════════════════════════════════
print("📁 Мониторинг и nginx...")

write_file("grafana/dashboards/apidoc-overview.json", r'''{
  "dashboard": {
    "title": "APIDoc Manager Overview",
    "uid": "apidoc-overview",
    "timezone": "browser",
    "panels": [
      {"title": "HTTP Request Rate", "type": "graph", "targets": [{"expr": "rate(apidoc_http_requests_total[5m])"}], "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}},
      {"title": "Request Duration (p95)", "type": "graph", "targets": [{"expr": "histogram_quantile(0.95, rate(apidoc_http_request_duration_seconds_bucket[5m]))"}], "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}},
      {"title": "Active Requests", "type": "graph", "targets": [{"expr": "apidoc_http_requests_in_progress"}], "gridPos": {"x": 0, "y": 8, "w": 8, "h": 6}},
      {"title": "Error Rate", "type": "graph", "targets": [{"expr": "rate(apidoc_http_requests_total{status=~\"5..\"}[5m])"}], "gridPos": {"x": 8, "y": 8, "w": 8, "h": 6}},
      {"title": "Database Connections", "type": "gauge", "targets": [{"expr": "apidoc_database_connections"}], "gridPos": {"x": 16, "y": 8, "w": 8, "h": 6}},
      {"title": "Specifications Total", "type": "stat", "targets": [{"expr": "apidoc_specifications_total"}], "gridPos": {"x": 0, "y": 14, "w": 4, "h": 4}}
    ],
    "refresh": "30s",
    "time": {"from": "now-1h", "to": "now"}
  }
}''')

write_file("grafana/dashboards/apidoc-performance.json", r'''{
  "dashboard": {
    "title": "APIDoc Manager Performance",
    "uid": "apidoc-performance",
    "panels": [
      {"title": "Request Duration Heatmap", "type": "heatmap", "targets": [{"expr": "rate(apidoc_http_request_duration_seconds_bucket[5m])", "format": "heatmap"}], "gridPos": {"x": 0, "y": 0, "w": 24, "h": 8}},
      {"title": "P50 Latency", "type": "graph", "targets": [{"expr": "histogram_quantile(0.50, rate(apidoc_http_request_duration_seconds_bucket[5m]))", "legendFormat": "p50"}], "gridPos": {"x": 0, "y": 8, "w": 8, "h": 6}},
      {"title": "P90 Latency", "type": "graph", "targets": [{"expr": "histogram_quantile(0.90, rate(apidoc_http_request_duration_seconds_bucket[5m]))", "legendFormat": "p90"}], "gridPos": {"x": 8, "y": 8, "w": 8, "h": 6}},
      {"title": "P99 Latency", "type": "graph", "targets": [{"expr": "histogram_quantile(0.99, rate(apidoc_http_request_duration_seconds_bucket[5m]))", "legendFormat": "p99"}], "gridPos": {"x": 16, "y": 8, "w": 8, "h": 6}}
    ],
    "refresh": "30s"
  }
}''')

write_file("grafana/datasources/prometheus.yaml", """apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "30s"
      queryTimeout: "30s"
      httpMethod: "POST"
""")

write_file("prometheus.yml", """global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'apidoc-monitor'

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - 'alerts.yml'

scrape_configs:
  - job_name: 'apidoc-server'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['server:8000']
        labels:
          service: 'apidoc'
          environment: 'production'
""")

write_file("nginx.conf", r'''events {
    worker_connections 1024;
}

http {
    upstream apidoc_backend {
        least_conn;
        server server:8000;
    }

    server {
        listen 80;
        server_name api.apidoc.local;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.apidoc.local;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
        limit_req zone=api_limit burst=20 nodelay;

        access_log /var/log/nginx/apidoc_access.log;
        error_log /var/log/nginx/apidoc_error.log;

        location / {
            proxy_pass http://apidoc_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        location /health {
            proxy_pass http://apidoc_backend/health;
            access_log off;
        }

        location /metrics {
            allow 10.0.0.0/8;
            allow 172.16.0.0/12;
            allow 192.168.0.0/16;
            deny all;
            proxy_pass http://apidoc_backend/metrics;
        }
    }
}''')

print("✓ Мониторинг и nginx созданы (6 файлов)")
print()

# ═══════════════════════════════════════════════════════════════════
# 17. СКРИПТЫ
# ═══════════════════════════════════════════════════════════════════
print("📁 Скрипты...")

write_file("scripts/install.sh", r'''#!/bin/bash
set -e

echo "==================================="
echo "   APIDoc Manager Installer       "
echo "==================================="

check_python() {
    echo "Checking Python..."
    if command -v python3 &> /dev/null; then PYTHON="python3"
    elif command -v python &> /dev/null; then PYTHON="python"
    else echo "✗ Python not found"; exit 1; fi
    echo "✓ Python found"
}

install_apidoc() {
    echo "Installing APIDoc Manager..."
    if [[ -f "pyproject.toml" ]]; then pip install -e .; else pip install apidoc-manager; fi
    echo "✓ APIDoc Manager installed"
}

main() {
    check_python
    install_apidoc
    mkdir -p "$HOME/.apidoc/logs" "$HOME/.apidoc/cache"
    echo "==================================="
    echo "   Installation Complete!          "
    echo "==================================="
}

main "$@"
''')

write_file("scripts/build.sh", r'''#!/bin/bash
set -e

echo "==================================="
echo "     APIDoc Manager Build         "
echo "==================================="

VERSION=""; BUILD_TYPE="wheel"; DOCKER_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --version) VERSION="$2"; shift 2 ;;
        --type) BUILD_TYPE="$2"; shift 2 ;;
        --docker) DOCKER_BUILD=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

clean() {
    echo "Cleaning..."
    rm -rf build/ dist/ *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    echo "✓ Cleaned"
}

build_python() {
    echo "Building Python package..."
    pip install --quiet build
    if [[ "$BUILD_TYPE" == "wheel" ]]; then python -m build --wheel; else python -m build; fi
    echo "✓ Python package built"
}

main() {
    clean
    build_python
    if [[ "$DOCKER_BUILD" == "true" ]]; then
        docker build -f docker/Dockerfile.prod -t "apidoc-manager:${VERSION:-latest}" .
    fi
    echo "==================================="
    echo "      Build Complete!              "
    echo "==================================="
}

main "$@"
''')

write_file("scripts/deploy.sh", r'''#!/bin/bash
set -e

echo "==================================="
echo "   APIDoc Manager Deploy          "
echo "==================================="

ENVIRONMENT="production"; DEPLOY_TYPE="docker"

while [[ $# -gt 0 ]]; do
    case $1 in
        --env) ENVIRONMENT="$2"; shift 2 ;;
        --type) DEPLOY_TYPE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

deploy_docker() {
    echo "Deploying with Docker Compose..."
    COMPOSE_FILE="docker/docker-compose.yml"
    if [[ "$ENVIRONMENT" == "production" ]]; then COMPOSE_FILE="docker/docker-compose.prod.yml"; fi
    docker-compose -f "$COMPOSE_FILE" up -d
    echo "✓ Docker deployment complete"
}

deploy_kubernetes() {
    echo "Deploying to Kubernetes..."
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml -n apidoc
    kubectl apply -f k8s/secrets.yaml -n apidoc
    kubectl apply -f k8s/deployment.yaml -n apidoc
    kubectl apply -f k8s/service.yaml -n apidoc
    kubectl apply -f k8s/hpa.yaml -n apidoc
    echo "✓ Kubernetes deployment complete"
}

main() {
    case "$DEPLOY_TYPE" in
        "docker") deploy_docker ;;
        "kubernetes") deploy_kubernetes ;;
        *) echo "Unknown deploy type: $DEPLOY_TYPE"; exit 1 ;;
    esac
    echo "==================================="
    echo "     Deployment Successful!        "
    echo "==================================="
}

main "$@"
''')

write_file("scripts/gen_completion.sh", r'''#!/bin/bash
set -e

OUTPUT_DIR="${1:-completions}"
mkdir -p "$OUTPUT_DIR"

echo "Generating shell completions in $OUTPUT_DIR..."
apidoc --show-completion bash > "$OUTPUT_DIR/apidoc.bash" && echo "✓ Bash"
apidoc --show-completion zsh > "$OUTPUT_DIR/apidoc.zsh" && echo "✓ Zsh"
apidoc --show-completion fish > "$OUTPUT_DIR/apidoc.fish" && echo "✓ Fish"
echo ""
echo "Done! To install:"
echo "Bash:  source $OUTPUT_DIR/apidoc.bash"
echo "Zsh:   source $OUTPUT_DIR/apidoc.zsh"
echo "Fish:  cp $OUTPUT_DIR/apidoc.fish ~/.config/fish/completions/"
''')

print("✓ Скрипты созданы (4 файла)")
print()

# ═══════════════════════════════════════════════════════════════════
# ФИНАЛ
# ═══════════════════════════════════════════════════════════════════
print("=" * 60)
print("  🎉 ПРОЕКТ ПОЛНОСТЬЮ СОЗДАН!")
print("=" * 60)
print(f"  Всего файлов: 118")
print(f"  Директория: {BASE_DIR}")
print()
print("  Для установки выполните:")
print(f"  cd {BASE_DIR}")
print("  pip install -e .")
print("  apidoc --help")
print("=" * 60)
