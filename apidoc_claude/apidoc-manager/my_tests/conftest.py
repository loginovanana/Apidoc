"""Shared fixtures."""
import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10) as c:
        yield c

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
