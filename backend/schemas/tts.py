from pydantic import BaseModel, ConfigDict, Field


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

    model_config = ConfigDict(extra="forbid")
