"""Pytest configuration."""

import pytest
import httpx


@pytest.fixture
def base_url():
    return "https://api.example.com/v1"


@pytest.fixture
async def client():
    async with httpx.AsyncClient() as client:
        yield client