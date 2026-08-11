import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import RiskLevel


class SymptomPayload(BaseModel):
    cold_sensitivity: bool
    hot_sensitivity: bool
    pressure_pain: bool
    spontaneous_pain: bool
    bleeding_gums: bool
    swollen_gums: bool
    receding_gums: bool
    black_spot: bool
    white_spot: bool
    yellow_staining: bool
    bad_breath: bool
    dry_mouth: bool
    mouth_ulcer: bool
    burning_sensation: bool
    loose_tooth: bool
    broken_tooth: bool
    brushes_twice_daily: bool
    uses_floss: bool
    sugary_diet: bool
    acid_exposure: bool

    model_config = ConfigDict(extra="forbid")


class AssessmentCreateRequest(BaseModel):
    symptoms: SymptomPayload
    photo_base64: str | None = None


class AssessmentResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    risk_level: RiskLevel

    model_config = ConfigDict(from_attributes=True)
