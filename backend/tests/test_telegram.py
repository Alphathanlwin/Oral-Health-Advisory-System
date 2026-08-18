import uuid
from unittest.mock import patch

import httpx
import pytest

from config import settings
from database import engine
from main import app

PASSWORD = "SecurePassword123"


@pytest.fixture(autouse=True)
async def _dispose_engine():
    yield
    await engine.dispose()


async def _client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


def _unique_email(prefix: str = "telegram") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}@example.com"


async def _register_and_login(client: httpx.AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "full_name": "Telegram User",
            "date_of_birth": "1990-05-15",
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    return login.json()["data"]["access_token"]


async def test_link_status_without_bot_username_has_no_deep_link():
    async with await _client() as client:
        token = await _register_and_login(client, _unique_email("link1"))
        headers = {"Authorization": f"Bearer {token}"}

        with patch.object(settings, "TELEGRAM_BOT_USERNAME", ""):
            response = await client.get("/api/v1/telegram/link", headers=headers)

        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data == {"linked": False, "deep_link": None}


async def test_link_status_with_bot_username_returns_deep_link():
    async with await _client() as client:
        token = await _register_and_login(client, _unique_email("link2"))
        headers = {"Authorization": f"Bearer {token}"}

        with patch.object(settings, "TELEGRAM_BOT_USERNAME", "ohas_test_bot"):
            response = await client.get("/api/v1/telegram/link", headers=headers)

        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["linked"] is False
        assert data["deep_link"].startswith("https://t.me/ohas_test_bot?start=")


async def test_webhook_links_account_via_start_token():
    async with await _client() as client:
        token = await _register_and_login(client, _unique_email("link3"))
        headers = {"Authorization": f"Bearer {token}"}

        with patch.object(settings, "TELEGRAM_BOT_USERNAME", "ohas_test_bot"):
            link_response = await client.get("/api/v1/telegram/link", headers=headers)
        deep_link = link_response.json()["data"]["deep_link"]
        start_token = deep_link.split("?start=")[1]

        webhook_response = await client.post(
            "/api/v1/telegram/webhook",
            json={
                "update_id": 1,
                "message": {
                    "message_id": 1,
                    "chat": {"id": 987654321},
                    "text": f"/start {start_token}",
                },
            },
        )
        assert webhook_response.status_code == 200, webhook_response.text

        status_response = await client.get("/api/v1/telegram/link", headers=headers)
        assert status_response.json()["data"]["linked"] is True


async def test_webhook_ignores_invalid_token():
    async with await _client() as client:
        token = await _register_and_login(client, _unique_email("link4"))
        headers = {"Authorization": f"Bearer {token}"}

        webhook_response = await client.post(
            "/api/v1/telegram/webhook",
            json={
                "update_id": 2,
                "message": {
                    "message_id": 2,
                    "chat": {"id": 111222333},
                    "text": "/start not-a-real-token",
                },
            },
        )
        assert webhook_response.status_code == 200, webhook_response.text

        status_response = await client.get("/api/v1/telegram/link", headers=headers)
        assert status_response.json()["data"]["linked"] is False


async def test_webhook_rejects_wrong_secret():
    async with await _client() as client:
        with patch.object(settings, "TELEGRAM_WEBHOOK_SECRET", "expected-secret"):
            response = await client.post(
                "/api/v1/telegram/webhook",
                json={"update_id": 3, "message": {"chat": {"id": 1}, "text": "/start x"}},
                headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
            )
        assert response.status_code == 401
