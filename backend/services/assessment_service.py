import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from models.assessment import Assessment
from models.enums import RiskLevel
from models.symptom_response import SymptomResponse
from schemas.assessment import AssessmentCreateRequest, AssessmentResponse
from services.cv_service import CVService, CVServiceUnavailableError
from utils.image_utils import decode_base64_image, save_image, validate_image


class AssessmentService:
    async def create(
        self,
        payload: AssessmentCreateRequest,
        user_id: uuid.UUID,
        db: AsyncSession,
        cv_service: CVService,
    ) -> AssessmentResponse:
        symptoms = dict(payload.symptoms.model_dump())
        photo_url = None
        image_analysis_result = None

        if payload.photo_base64:
            image_bytes = decode_base64_image(payload.photo_base64)
            image = validate_image(image_bytes)
            photo_url = save_image(image_bytes, image.format)

            try:
                cv_response = await cv_service.analyze(image_bytes)
                image_analysis_result = cv_response
                for symptom_key in cv_service.extract_symptoms(cv_response):
                    symptoms[symptom_key] = True
            except CVServiceUnavailableError:
                # Graceful fallback: keep the saved photo, proceed with the
                # user-submitted symptoms only.
                image_analysis_result = {"status": "CV_SERVICE_UNAVAILABLE"}

        # Diagnosis engine is not implemented yet (Phase 3) — stub stores the
        # symptoms (merged with any CV-detected ones) and returns a
        # placeholder risk level.
        assessment = Assessment(
            user_id=user_id,
            risk_level=RiskLevel.LOW,
            photo_url=photo_url,
            image_analysis_result=image_analysis_result,
        )
        assessment.symptom_responses = [
            SymptomResponse(symptom_key=key, value=value) for key, value in symptoms.items()
        ]

        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        return AssessmentResponse.model_validate(assessment)
