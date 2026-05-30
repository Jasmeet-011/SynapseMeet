"""Auth endpoint tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register
        register_response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@synapsemeet.com", "password": "securepass123", "full_name": "Test User"},
        )
        assert register_response.status_code == 201
        data = register_response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@synapsemeet.com"

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@synapsemeet.com", "password": "securepass123"},
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@synapsemeet.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_registration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"email": "dup@synapsemeet.com", "password": "pass123", "full_name": "Dup"}
        await client.post("/api/v1/auth/register", json=payload)
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409
