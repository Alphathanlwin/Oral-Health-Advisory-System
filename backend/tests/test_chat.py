import uuid
from unittest.mock import patch

import httpx
import pytest

from database import engine
from main import app
from models.base import Base

PASSWORD = "SecurePassword123"


@pytest.fixture(autouse=True)
async def _dispose_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


async def _client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


def _unique_email(prefix: str = "chat") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}@example.com"


async def _register_and_login(client: httpx.AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "full_name": "Chat User",
            "date_of_birth": "1990-05-15",
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    return login.json()["data"]["access_token"]


def _all_false_symptoms(**overrides: bool) -> dict:
    symptoms = {
        "cold_sensitivity": False,
        "hot_sensitivity": False,
        "pressure_pain": False,
        "spontaneous_pain": False,
        "bleeding_gums": False,
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
        "brushes_twice_daily": False,
        "uses_floss": False,
        "sugary_diet": False,
        "acid_exposure": False,
    }
    symptoms.update(overrides)
    return symptoms


async def test_chat_intake_extracts_symptoms():
    async with await _client() as client:
        token = await _register_and_login(client, _unique_email("intake"))
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "services.llm_service.LLMService.complete",
            return_value='{"symptoms": {"cold_sensitivity": true, "bleeding_gums": false}}',
        ):
            response = await client.post(
                "/api/v1/chat/intake",
                json={"text": "My tooth hurts when I drink something cold, gums are fine."},
                headers=headers,
            )

        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["symptoms"] == {"cold_sensitivity": True, "bleeding_gums": False}
        assert data["unrecognized"] == []


async def test_chat_intake_drops_unrecognized_keys():
    async with await _client() as client:
        token = await _register_and_login(client, _unique_email("intake2"))
        headers = {"Authorization": f"Bearer {token}"}

        with patch(
            "services.llm_service.LLMService.complete",
            return_value='{"symptoms": {"cold_sensitivity": true, "not_a_real_symptom": true}}',
        ):
            response = await client.post(
                "/api/v1/chat/intake",
                json={"text": "Cold sensitivity and something weird."},
                headers=headers,
            )

        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["symptoms"] == {"cold_sensitivity": True}
        assert data["unrecognized"] == ["not_a_real_symptom"]


async def test_chat_intake_unconfigured_llm_returns_503():
    async with await _client() as client:
        token = await _register_and_login(client, _unique_email("intake3"))
        headers = {"Authorization": f"Bearer {token}"}

        # No LLM_API_KEY configured in the test environment, so the real
        # LLMService.complete() should raise LLMServiceUnavailableError.
        response = await client.post(
            "/api/v1/chat/intake",
            json={"text": "My tooth hurts."},
            headers=headers,
        )

        assert response.status_code == 503, response.text
        assert response.json()["error"]["code"] == "LLM_SERVICE_UNAVAILABLE"


async def test_chat_explain_grounded_answer():
    async with await _client() as client:
        token = await _register_and_login(client, _unique_email("explain"))
        headers = {"Authorization": f"Bearer {token}"}

        create_response = await client.post(
            "/api/v1/assessments/",
            json={
                "symptoms": _all_false_symptoms(bleeding_gums=True, swollen_gums=True),
                "photos": {"front": None, "upper": None, "lower": None},
            },
            headers=headers,
        )
        assert create_response.status_code == 201, create_response.text
        assessment_id = create_response.json()["data"]["id"]
        assert create_response.json()["data"]["diagnoses"], create_response.text

        with patch(
            "services.llm_service.LLMService.complete",
            return_value="Your gums bled because gingivitis was detected from your symptoms.",
        ) as mock_complete:
            response = await client.post(
                "/api/v1/chat/explain",
                json={"assessment_id": assessment_id, "question": "Why did I get this result?"},
                headers=headers,
            )

        assert response.status_code == 200, response.text
        assert "gingivitis" in response.json()["data"]["answer"].lower()
        # The grounding context passed to the LLM must include this
        # assessment's own diagnosis data, not a generic prompt.
        system_prompt = mock_complete.call_args.kwargs["system_prompt"]
        assert "GINGIVITIS" in system_prompt


async def test_chat_explain_rejects_other_users_assessment():
    async with await _client() as client:
        owner_token = await _register_and_login(client, _unique_email("explain_owner"))
        other_token = await _register_and_login(client, _unique_email("explain_other"))

        create_response = await client.post(
            "/api/v1/assessments/",
            json={
                "symptoms": _all_false_symptoms(bleeding_gums=True, swollen_gums=True),
                "photos": {"front": None, "upper": None, "lower": None},
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assessment_id = create_response.json()["data"]["id"]

        response = await client.post(
            "/api/v1/chat/explain",
            json={"assessment_id": assessment_id, "question": "Why?"},
            headers={"Authorization": f"Bearer {other_token}"},
        )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"
