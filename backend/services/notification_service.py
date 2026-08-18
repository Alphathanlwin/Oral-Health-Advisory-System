import logging

import httpx

from config import settings
from schemas.assessment import AssessmentResponse

logger = logging.getLogger(__name__)


class NotificationService:
    """Telegram Bot API delivery. Every public method here is designed to be
    called fire-and-forget (e.g. via asyncio.create_task) — it never raises,
    it only logs, so a Telegram outage or missing bot token can never fail
    or delay the request that triggered it.
    """

    async def send_message(self, chat_id: str, text: str) -> None:
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.info("Telegram bot token not configured; skipping sendMessage.")
            return

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Telegram sendMessage failed for chat_id=%s: %s", chat_id, exc)

    async def send_assessment_report(self, chat_id: str, assessment: AssessmentResponse) -> None:
        lines = [
            "🦷 Your OHAS assessment is ready.",
            f"Risk level: {assessment.risk_level.value}",
            "",
        ]
        if not assessment.diagnoses:
            lines.append("No conditions were detected.")
        else:
            for diagnosis in assessment.diagnoses:
                lines.append(f"• {diagnosis.condition.value.replace('_', ' ').title()}")
                for rec in diagnosis.recommendations:
                    lines.append(f"   - {rec.action} ({rec.urgency.value.replace('_', ' ').title()})")
        lines.append("")
        lines.append("This is not a medical diagnosis. Consult a licensed dentist.")

        await self.send_message(chat_id, "\n".join(lines))
