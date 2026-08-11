import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class SymptomResponse(Base):
    __tablename__ = "symptom_responses"
    __table_args__ = (UniqueConstraint("assessment_id", "symptom_key"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False
    )
    symptom_key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[bool] = mapped_column(Boolean, nullable=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="symptom_responses")
