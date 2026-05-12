"""Pytest configuration."""

import pytest
import httpx


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8766"


@pytest.fixture
async def client():
    async with httpx.AsyncClient() as client:
        yield client