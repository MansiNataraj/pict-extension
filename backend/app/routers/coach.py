"""Legacy web-app endpoint: check a draft message against the CRT for a recipient role."""
from fastapi import APIRouter, HTTPException
from app.chains import execute_llm_chain
from app.models import CoachRequest, CoachResponse
from app.prompts import get_coaching_prompt
from config import SUPPORTED_LANGUAGES

router = APIRouter(prefix="/coach", tags=["Message Coach"])


@router.post("", response_model=CoachResponse)
@router.post("/", response_model=CoachResponse, include_in_schema=False)
async def coach_draft(req: CoachRequest):
    lang = SUPPORTED_LANGUAGES.get(req.language_code)
    if not lang:
        raise HTTPException(status_code=400, detail="Unsupported language code")

    prompt = get_coaching_prompt(lang["name"], req.draft_message, req.recipient_role)
    try:
        result, model = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)
        return CoachResponse(
            is_risky=bool(result.get("is_risky", False)),
            risk_level=result.get("risk_level", "green"),
            crt_code=result.get("crt_code"),
            warning_message=result.get("warning_message"),
            clarification_question=result.get("clarification_question"),
            variants=result.get("variants"),
            predicted_reactions=result.get("predicted_reactions"),
            model_used=model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coaching failed: {e}")
