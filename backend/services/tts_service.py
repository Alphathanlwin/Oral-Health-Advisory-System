import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

# "Rachel" — a warm, expressive default ElevenLabs voice, used when
# ELEVENLABS_VOICE_ID isn't set.
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


class TTSServiceUnavailableError(Exception):
    """Raised when the ElevenLabs TTS API cannot be reached, errors, or is unconfigured."""


class TTSService:
    async def synthesize(self, text: str) -> bytes:
        """Calls the ElevenLabs text-to-speech API for the given text.

        Raises TTSServiceUnavailableError if no API key is configured or on any
        network/API failure, so callers (the frontend) can fall back to the
        browser's built-in speech synthesis instead of failing silently.
        """
        if not settings.ELEVENLABS_API_KEY:
            raise TTSServiceUnavailableError()

        voice_id = settings.ELEVENLABS_VOICE_ID or DEFAULT_VOICE_ID
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.85,
                "style": 0.6,
                "use_speaker_boost": True,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as exc:
            logger.warning("ElevenLabs TTS service unavailable: %s", exc)
            raise TTSServiceUnavailableError() from exc
