from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from exceptions import LLMServiceUnavailableException
from models.user import User
from schemas.chat import ChatExplainRequest, ChatIntakeRequest
from services.assessment_service import AssessmentService
from services.chat_explain_service import ChatExplainService
from services.chat_intake_service import ChatIntakeService
from services.llm_service import LLMService, LLMServiceUnavailableError
from utils.response import success_response

router = APIRouter()


@router.post("/intake")
async def chat_intake(
    payload: ChatIntakeRequest,
    current_user: User = Depends(get_current_user),
    chat_intake_service: ChatIntakeService = Depends(ChatIntakeService),
    llm_service: LLMService = Depends(LLMService),
):
    try:
        result = await chat_intake_service.extract(payload.text, llm_service)
    except LLMServiceUnavailableError:
        raise LLMServiceUnavailableException()

    return success_response(
        data=result.model_dump(),
        message="Symptoms extracted successfully.",
    )


@router.post("/explain")
async def chat_explain(
    payload: ChatExplainRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    assessment_service: AssessmentService = Depends(AssessmentService),
    chat_explain_service: ChatExplainService = Depends(ChatExplainService),
    llm_service: LLMService = Depends(LLMService),
):
    try:
        result = await chat_explain_service.explain(
            payload.assessment_id,
            payload.question,
            current_user.id,
            db,
            assessment_service,
            llm_service,
        )
    except LLMServiceUnavailableError:
        raise LLMServiceUnavailableException()

    return success_response(
        data=result.model_dump(),
        message="Answer generated successfully.",
    )
