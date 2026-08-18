from pydantic import BaseModel, ConfigDict, Field


class ChatIntakeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

    model_config = ConfigDict(extra="forbid")


class ChatIntakeResponse(BaseModel):
    # Only the symptom keys the free-text description actually implied —
    # omitted keys mean "not mentioned", not "false", so the frontend only
    # overwrites the toggles the user actually talked about.
    symptoms: dict[str, bool]
    unrecognized: list[str] = []


class ChatExplainRequest(BaseModel):
    assessment_id: str
    question: str = Field(..., min_length=1, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class ChatExplainResponse(BaseModel):
    answer: str
