"""Legacy web-app endpoint: ghostwrite a culturally calibrated reply to reach a goal."""
from fastapi import APIRouter, HTTPException
from app.chains import execute_llm_chain
from app.models import ReplyRequest, ReplyResponse
from app.prompts import get_reply_ghostwriter_prompt
from config import SUPPORTED_LANGUAGES

router = APIRouter(prefix="/reply", tags=["Smart Reply"])


@router.post("", response_model=ReplyResponse)
@router.post("/", response_model=ReplyResponse, include_in_schema=False)
async def suggest_reply(req: ReplyRequest):
    lang = SUPPORTED_LANGUAGES.get(req.language_code)
    if not lang:
        raise HTTPException(status_code=400, detail="Unsupported language code")

    prompt = get_reply_ghostwriter_prompt(lang["name"], req.conversation_history, req.goal)
    try:
        result, model = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reply generation failed: {e}")

    return ReplyResponse(
        suggested_reply=result.get("suggested_reply", ""),
        diplomatic_rationale=result.get("diplomatic_rationale", "Aligned with diplomatic goals."),
        model_used=model,
    )
