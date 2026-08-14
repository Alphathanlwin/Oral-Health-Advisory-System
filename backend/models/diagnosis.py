import uuid

from sqlalchemy import ForeignKey, Text, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.enums import Condition


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False
    )
    condition: Mapped[Condition] = mapped_column(SAEnum(Condition), nullable=False)
    triggered_rules: Mapped[list] = mapped_column(JSONB, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="diagnoses")
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="diagnosis", cascade="all, delete-orphan"
    )
