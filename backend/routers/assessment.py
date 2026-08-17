from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from dependencies import get_current_user
from models.assessment import Assessment
from models.diagnosis import Diagnosis
from models.user import User
from schemas.assessment import (
    AssessmentCreateRequest,
    AssessmentResponse,
    AssessmentSummaryResponse,
)
from services.assessment_service import AssessmentService
from services.cv_service import CVService
from services.prolog_service import PrologService
from utils.response import success_response

router = APIRouter()


@router.get("/")
async def list_assessments(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_query = select(func.count(Assessment.id)).where(Assessment.user_id == current_user.id)
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    offset = (page - 1) * size
    statement = (
        select(Assessment)
        .where(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .offset(offset)
        .limit(size)
        .options(selectinload(Assessment.diagnoses))
    )
    result = await db.execute(statement)
    assessments = result.scalars().all()

    items = []
    for assessment in assessments:
        items.append(
            AssessmentSummaryResponse(
                id=assessment.id,
                created_at=assessment.created_at,
                risk_level=assessment.risk_level,
                conditions_detected=[diagnosis.condition for diagnosis in assessment.diagnoses],
            ).model_dump(mode="json")
        )

    return success_response(
        data={"items": items, "total": total, "page": page, "size": size},
        message=None,
    )


@router.get("/{assessment_id}")
async def get_assessment_detail(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    statement = (
        select(Assessment)
        .where(Assessment.id == assessment_id)
        .options(
            selectinload(Assessment.diagnoses).selectinload(Diagnosis.recommendations),
        )
    )
    result = await db.execute(statement)
    assessment = result.scalar_one_or_none()

    if assessment is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "ASSESSMENT_NOT_FOUND", "message": "Assessment not found."},
        )

    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You do not have access to this assessment."},
        )

    return success_response(
        data=AssessmentResponse.model_validate(assessment).model_dump(mode="json"),
        message=None,
    )


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
