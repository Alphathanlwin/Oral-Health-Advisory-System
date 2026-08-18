from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from dependencies import get_current_user
from exceptions import UnauthorizedException
from models.user import User
from services.notification_service import NotificationService
from services.telegram_link_service import TelegramLinkService
from utils.response import success_response

router = APIRouter()


@router.get("/link")
async def get_telegram_link(
    current_user: User = Depends(get_current_user),
    telegram_link_service: TelegramLinkService = Depends(TelegramLinkService),
):
    result = telegram_link_service.get_link_status(current_user)
    return success_response(
        data=result.model_dump(),
        message="Telegram link status retrieved successfully.",
    )


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_link_service: TelegramLinkService = Depends(TelegramLinkService),
    notification_service: NotificationService = Depends(NotificationService),
):
    # Telegram lets you set a secret token it echoes back on every webhook
    # call, so this endpoint can reject requests that aren't actually from
    # Telegram. Only enforced once TELEGRAM_WEBHOOK_SECRET is configured, so
    # local development without a public webhook URL isn't blocked.
    if settings.TELEGRAM_WEBHOOK_SECRET:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != settings.TELEGRAM_WEBHOOK_SECRET:
            raise UnauthorizedException()

    update = await request.json()
    await telegram_link_service.handle_update(update, db, notification_service)
    # Telegram only cares about the HTTP status, not the body.
    return success_response(message="ok")
