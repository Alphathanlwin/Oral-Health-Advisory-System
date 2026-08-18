from pydantic import BaseModel


class TelegramLinkResponse(BaseModel):
    linked: bool
    deep_link: str | None = None
