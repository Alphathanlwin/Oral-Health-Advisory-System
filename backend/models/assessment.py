import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.enums import RiskLevel


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    risk_level: Mapped[RiskLevel] = mapped_column(SAEnum(RiskLevel), nullable=False)
    # {"front": "uploads/....jpg", "upper": null, "lower": null} — each slot
    # optional/nullable (Phase 3D: multi-photo guided capture replaced the
    # single photo_url column).
    photo_urls: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # {"front": <HF response|status>, "upper": ..., "lower": ...}
    image_analysis_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="assessments")
    symptom_responses: Mapped[list["SymptomResponse"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    diagnoses: Mapped[list["Diagnosis"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
