from fastapi import APIRouter, HTTPException
from app.models import CoachRequest, CoachResponse, FormalityVariant, WhatIfBranch
from app.prompts import get_coach_prompt
from app.chains import execute_llm_chain
from config import SUPPORTED_LANGUAGES

router = APIRouter(prefix="/coach", tags=["Message Coach"])

@router.post("", response_model=CoachResponse)
@router.post("/", response_model=CoachResponse)
async def coach_single_message(payload: CoachRequest):
    lang_info = SUPPORTED_LANGUAGES.get(payload.language_code)
    if not lang_info:
        raise HTTPException(status_code=400, detail="Unsupported language code")

    prompt = get_coach_prompt(
        source_text=payload.source_text,
        language_name=lang_info["name"],
        intent=payload.intent.model_dump(),
        answers=payload.clarification_answers
    )

    try:
        result, model_used = await execute_llm_chain(
            prompt, 
            temperature=0.2, 
            provider=payload.provider
        )

        variants_data = [FormalityVariant(**v) for v in result.get("variants", [])]
        branches_data = [WhatIfBranch(**b) for b in result.get("branches", [])]

        return CoachResponse(
            session_id=payload.session_id,
            needs_clarification=bool(result.get("needs_clarification", False)),
            clarification_questions=result.get("clarification_questions", []),
            clarification_reason=result.get("clarification_reason"),
            primary_translation=result.get("primary_translation"),
            variants=variants_data,
            branches=branches_data,
            cultural_notes=result.get("cultural_notes"),
            model_used=model_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coach engine error: {str(e)}")