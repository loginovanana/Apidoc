"""Tests for users endpoints."""

import pytest
from httpx import AsyncClient


class TestUsersAPI:
    """Test cases for users endpoints."""
    

    @pytest.mark.asyncio
    async def test_listUsers(self, client: AsyncClient, base_url: str):
        """Test GET /users"""
        response = await client.get(f"{base_url}/users")
        assert response.status_code == 200


    @pytest.mark.asyncio
    async def test_createUser(self, client: AsyncClient, base_url: str):
        """Test POST /users"""
        response = await client.post(f"{base_url}/users")
        assert response.status_code == 201
