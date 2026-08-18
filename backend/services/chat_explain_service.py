import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.assessment import AssessmentResponse
from schemas.chat import ChatExplainResponse
from services.assessment_service import AssessmentService
from services.llm_service import LLMService

REFUSAL = (
    "I can only answer questions about this assessment's own results. Please "
    "ask about the conditions detected, why they were flagged, or the "
    "recommended next steps shown on this page."
)

SYSTEM_PROMPT_TEMPLATE = (
    "You are Dr. Ava's explainer assistant. You never diagnose, never suggest "
    "conditions beyond what is listed below, and never give medical advice "
    "outside this data. This assessment's result (the sole source of truth — "
    "Prolog already produced it; you only explain it in plain language):\n\n"
    "{context}\n\n"
    "Answer the user's question using ONLY the information above. If the "
    "question asks about anything not covered by this data (a different "
    "condition, a new diagnosis, general medical advice, or anything "
    f'unrelated), reply with exactly: "{REFUSAL}"'
)


def _build_context(assessment: AssessmentResponse) -> str:
    if not assessment.diagnoses:
        return f"Risk level: {assessment.risk_level.value}\nNo conditions were detected."

    lines = [f"Risk level: {assessment.risk_level.value}", ""]
    for diagnosis in assessment.diagnoses:
        lines.append(f"Condition: {diagnosis.condition.value}")
        lines.append(f"Explanation: {diagnosis.explanation}")
        lines.append(f"Triggered rules: {', '.join(diagnosis.triggered_rules)}")
        for rec in diagnosis.recommendations:
            lines.append(f"Recommendation ({rec.urgency.value}): {rec.action}")
        lines.append("")
    return "\n".join(lines)


class ChatExplainService:
    async def explain(
        self,
        assessment_id: str,
        question: str,
        user_id: uuid.UUID,
        db: AsyncSession,
        assessment_service: AssessmentService,
        llm_service: LLMService,
    ) -> ChatExplainResponse:
        """Answers a question grounded strictly in one assessment's own data.

        Reuses AssessmentService.get_for_user so ownership/404 handling stays
        identical to the rest of the assessment endpoints. Raises
        LLMServiceUnavailableError (propagated from llm_service) on any LLM
        failure so the router can surface a consistent 503.
        """
        assessment = await assessment_service.get_for_user(assessment_id, user_id, db)
        context = _build_context(assessment)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)

        answer = await llm_service.complete(
            system_prompt=system_prompt,
            user_message=question,
            max_tokens=400,
        )
        return ChatExplainResponse(answer=answer.strip())
