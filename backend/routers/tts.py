from fastapi import APIRouter, Depends
from fastapi.responses import Response

from dependencies import get_current_user
from exceptions import TTSServiceUnavailableException
from models.user import User
from schemas.tts import TTSRequest
from services.tts_service import TTSService, TTSServiceUnavailableError

router = APIRouter()


@router.post("/")
async def synthesize_speech(
    payload: TTSRequest,
    current_user: User = Depends(get_current_user),
    tts_service: TTSService = Depends(TTSService),
):
    try:
        audio_bytes = await tts_service.synthesize(payload.text)
    except TTSServiceUnavailableError:
        raise TTSServiceUnavailableException()

    return Response(content=audio_bytes, media_type="audio/mpeg")
