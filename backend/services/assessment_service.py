import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from models.assessment import Assessment
from models.enums import RiskLevel
from models.symptom_response import SymptomResponse
from schemas.assessment import AssessmentCreateRequest, AssessmentResponse


class AssessmentService:
    async def create(
        self, payload: AssessmentCreateRequest, user_id: uuid.UUID, db: AsyncSession
    ) -> AssessmentResponse:
        # Diagnosis engine is not implemented yet (Phase 3) — stub stores the
        # raw symptoms and returns a placeholder risk level.
        assessment = Assessment(user_id=user_id, risk_level=RiskLevel.LOW)
        assessment.symptom_responses = [
            SymptomResponse(symptom_key=key, value=value)
            for key, value in payload.symptoms.model_dump().items()
        ]

        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        return AssessmentResponse.model_validate(assessment)
