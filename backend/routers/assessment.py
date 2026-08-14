from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.assessment import AssessmentCreateRequest, AssessmentResponse
from services.assessment_service import AssessmentService
from services.cv_service import CVService
from services.prolog_service import PrologService
from utils.response import success_response

router = APIRouter()


@router.post("/", status_code=201)
async def create_assessment(
    payload: AssessmentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    assessment_service: AssessmentService = Depends(AssessmentService),
    cv_service: CVService = Depends(CVService),
    prolog_service: PrologService = Depends(PrologService),
):
    assessment = await assessment_service.create(
        payload, current_user.id, db, cv_service, prolog_service
    )
    return success_response(
        data=assessment.model_dump(mode="json"),
        message="Assessment saved successfully.",
    )
