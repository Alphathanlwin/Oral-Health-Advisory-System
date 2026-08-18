import uuid
from unittest.mock import patch

import httpx
import pytest

from database import engine
from main import app

PASSWORD = "SecurePassword123"


@pytest.fixture(autouse=True)
async def _dispose_engine():
    yield
    await engine.dispose()


async def _client() -> httpx.AsyncClient:
    # raise_app_exceptions=False: Starlette's ServerErrorMiddleware always
    # re-raises the original exception after building the 500 response (so
    # real servers can log it) — the default True here would propagate that
    # re-raise into the test instead of returning the response our global
    # exception handler already built.
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


def _unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:12]}@example.com"


async def test_health_check():
    async with await _client() as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


async def test_register_login_flow():
    email = _unique_email()
    async with await _client() as client:
        register = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": PASSWORD,
                "full_name": "Test User",
                "date_of_birth": "1990-05-15",
            },
        )
        assert register.status_code == 201
        body = register.json()
        assert body["success"] is True
        assert body["data"]["email"] == email
        assert body["data"]["full_name"] == "Test User"

        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": PASSWORD},
        )
        assert login.status_code == 200
        token = login.json()["data"]
        assert token["token_type"] == "bearer"
        assert token["access_token"]
        assert token["expires_in"] == 3600


async def test_register_duplicate_email_conflict():
    email = _unique_email()
    payload = {
        "email": email,
        "password": PASSWORD,
        "full_name": "Test User",
    }
    async with await _client() as client:
        assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201

        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


async def test_login_invalid_credentials():
    async with await _client() as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": _unique_email(), "password": "WrongPassword123"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_register_rejects_short_password():
    async with await _client() as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": _unique_email(), "password": "short", "full_name": "Short Pass"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_unhandled_exception_returns_standard_error_response():
    async with await _client() as client:
        with patch("routers.auth.AuthService.register", side_effect=RuntimeError("boom")):
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": _unique_email(),
                    "password": PASSWORD,
                    "full_name": "Test User",
                    "date_of_birth": "1990-05-15",
                },
            )

        assert response.status_code == 500
        assert response.json()["success"] is False
        assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
