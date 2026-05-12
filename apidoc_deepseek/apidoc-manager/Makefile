.PHONY: help install dev test lint format clean build docker-build docker-up docker-down

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
