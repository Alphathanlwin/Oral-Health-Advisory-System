import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.user import User
from schemas.telegram import TelegramLinkResponse
from services.notification_service import NotificationService
from utils.security import create_purpose_token, decode_purpose_token

LINK_TOKEN_PURPOSE = "telegram_link"
LINK_TOKEN_EXPIRE_MINUTES = 15


class TelegramLinkService:
    def _build_deep_link(self, user_id: uuid.UUID) -> str | None:
        if not settings.TELEGRAM_BOT_USERNAME:
            return None
        token = create_purpose_token(str(user_id), LINK_TOKEN_PURPOSE, LINK_TOKEN_EXPIRE_MINUTES)
        return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={token}"

    def get_link_status(self, user: User) -> TelegramLinkResponse:
        return TelegramLinkResponse(
            linked=bool(user.telegram_chat_id),
            deep_link=self._build_deep_link(user.id),
        )

    async def handle_update(
        self,
        update: dict,
        db: AsyncSession,
        notification_service: NotificationService,
    ) -> None:
        """Handles a Telegram `/start <token>` deep-link message. Never raises
        — a webhook must always return 200 to Telegram regardless of whether
        the token was valid, so any failure here is logged, not surfaced.
        """
        message = update.get("message") or {}
        text = (message.get("text") or "").strip()
        chat = message.get("chat") or {}
        chat_id = chat.get("id")

        if chat_id is None or not text.startswith("/start"):
            return

        parts = text.split(maxsplit=1)
        if len(parts) != 2:
            return

        user_id = decode_purpose_token(parts[1].strip(), LINK_TOKEN_PURPOSE)
        if user_id is None:
            await notification_service.send_message(
                str(chat_id),
                "This link is invalid or has expired. Please generate a new one from OHAS.",
            )
            return

        user = await db.get(User, user_id)
        if user is None:
            return

        user.telegram_chat_id = str(chat_id)
        await db.commit()

        await notification_service.send_message(
            str(chat_id),
            "✅ Your Telegram account is now linked to OHAS. You'll receive your assessment reports here.",
        )
