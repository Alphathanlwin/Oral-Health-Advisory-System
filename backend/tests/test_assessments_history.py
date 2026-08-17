import uuid

import httpx
import pytest

from database import engine
from main import app
from models.base import Base


@pytest.fixture(autouse=True)
async def _dispose_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


async def _client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


def _unique_email(prefix: str = "user") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}@example.com"


async def _register_and_login(client: httpx.AsyncClient, email: str, password: str = "SecurePassword123") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "History User",
            "date_of_birth": "1990-05-15",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return login.json()["data"]["access_token"]


async def test_user_can_list_and_fetch_own_assessments():
    email = _unique_email("history_owner")
    async with await _client() as client:
        token = await _register_and_login(client, email)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "symptoms": {
                "cold_sensitivity": False,
                "hot_sensitivity": False,
                "pressure_pain": False,
                "spontaneous_pain": False,
                "bleeding_gums": True,
                "swollen_gums": False,
                "receding_gums": False,
                "black_spot": False,
                "white_spot": False,
                "yellow_staining": False,
                "bad_breath": False,
                "dry_mouth": False,
                "mouth_ulcer": False,
                "burning_sensation": False,
                "loose_tooth": False,
                "broken_tooth": False,
                "brushes_twice_daily": True,
                "uses_floss": False,
                "sugary_diet": False,
                "acid_exposure": False,
            },
            "photos": {"front": None, "upper": None, "lower": None},
        }

        create_response = await client.post(
            "/api/v1/assessments/",
            json=payload,
            headers=headers,
        )
        assert create_response.status_code == 201, create_response.text
        assessment_id = create_response.json()["data"]["id"]

        list_response = await client.get("/api/v1/assessments/?page=1&size=10", headers=headers)
        assert list_response.status_code == 200, list_response.text
        body = list_response.json()["data"]
        assert body["total"] >= 1
        assert body["page"] == 1
        assert body["size"] == 10
        assert any(item["id"] == assessment_id for item in body["items"])

        detail_response = await client.get(f"/api/v1/assessments/{assessment_id}", headers=headers)
        assert detail_response.status_code == 200, detail_response.text
        detail = detail_response.json()["data"]
        assert detail["id"] == assessment_id
        assert detail["diagnoses"]


async def test_other_user_cannot_access_someone_else_assessment():
    owner_email = _unique_email("history_owner_2")
    other_email = _unique_email("history_other_2")
    async with await _client() as client:
        owner_token = await _register_and_login(client, owner_email)
        other_token = await _register_and_login(client, other_email)

        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        other_headers = {"Authorization": f"Bearer {other_token}"}

        payload = {
            "symptoms": {
                "cold_sensitivity": False,
                "hot_sensitivity": False,
                "pressure_pain": False,
                "spontaneous_pain": False,
                "bleeding_gums": True,
                "swollen_gums": False,
                "receding_gums": False,
                "black_spot": False,
                "white_spot": False,
                "yellow_staining": False,
                "bad_breath": False,
                "dry_mouth": False,
                "mouth_ulcer": False,
                "burning_sensation": False,
                "loose_tooth": False,
                "broken_tooth": False,
                "brushes_twice_daily": True,
                "uses_floss": False,
                "sugary_diet": False,
                "acid_exposure": False,
            },
            "photos": {"front": None, "upper": None, "lower": None},
        }

        create_response = await client.post(
            "/api/v1/assessments/",
            json=payload,
            headers=owner_headers,
        )
        assessment_id = create_response.json()["data"]["id"]

        forbidden = await client.get(f"/api/v1/assessments/{assessment_id}", headers=other_headers)
        assert forbidden.status_code == 403
        assert forbidden.json()["error"]["code"] == "FORBIDDEN"
