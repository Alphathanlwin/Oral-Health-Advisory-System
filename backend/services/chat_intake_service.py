import json
import logging

from schemas.assessment import SymptomPayload
from schemas.chat import ChatIntakeResponse
from services.llm_service import LLMService, LLMServiceUnavailableError

logger = logging.getLogger(__name__)

ALLOWED_SYMPTOM_KEYS = list(SymptomPayload.model_fields.keys())

SYSTEM_PROMPT = (
    "You extract dental symptom mentions from a patient's free-text description. "
    "You do not diagnose, explain conditions, or give medical advice — you only "
    "detect which of the following symptom keys the text explicitly implies:\n"
    f"{', '.join(ALLOWED_SYMPTOM_KEYS)}\n\n"
    "Respond with ONLY a JSON object (no markdown, no prose) of the form "
    '{"symptoms": {"<key>": true|false}}. Include a key ONLY if the text '
    "clearly implies that symptom is present (true) or explicitly denies it "
    "(false). Omit any key the text doesn't address — never guess. Use only "
    "keys from the list above; never invent new keys."
)


class ChatIntakeService:
    async def extract(self, text: str, llm_service: LLMService) -> ChatIntakeResponse:
        """Parses free-text symptom descriptions into validated symptoms{} keys.

        Raises LLMServiceUnavailableError (propagated from llm_service, or
        raised here on a malformed/unparseable model response) so the router
        can surface a consistent 503.
        """
        try:
            raw_reply = await llm_service.complete(
                system_prompt=SYSTEM_PROMPT,
                user_message=text,
                max_tokens=400,
            )
            parsed = json.loads(raw_reply)
            extracted = parsed["symptoms"]
            if not isinstance(extracted, dict):
                raise ValueError("symptoms must be an object")
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning("Chat intake: unparseable LLM response: %s", exc)
            raise LLMServiceUnavailableError() from exc

        symptoms: dict[str, bool] = {}
        unrecognized: list[str] = []
        for key, value in extracted.items():
            if key not in ALLOWED_SYMPTOM_KEYS:
                unrecognized.append(key)
                continue
            symptoms[key] = bool(value)

        return ChatIntakeResponse(symptoms=symptoms, unrecognized=unrecognized)
