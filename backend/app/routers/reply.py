from fastapi import APIRouter, HTTPException
from app.models import SmartReplyRequest, SmartReplyResponse
from app.prompts import get_reply_prompt
from app.chains import execute_llm_chain
from config import SUPPORTED_LANGUAGES

router = APIRouter(prefix="/reply", tags=["Smart Reply"])

@router.post("", response_model=SmartReplyResponse)
@router.post("/", response_model=SmartReplyResponse)
async def generate_smart_reply(payload: SmartReplyRequest):
    lang_info = SUPPORTED_LANGUAGES.get(payload.language_code)
    if not lang_info:
        raise HTTPException(status_code=400, detail="Unsupported language code")

    thread_lines = [f"{msg.speaker}: {msg.message}" for msg in payload.thread]
    thread_text = "\n".join(thread_lines)

    prompt = get_reply_prompt(
        language_name=lang_info["name"],
        thread_text=thread_text,
        goal=payload.goal
    )

    try:
        result, model_used = await execute_llm_chain(
            prompt, 
            temperature=0.3, 
            provider=payload.provider
        )
        return SmartReplyResponse(
            session_id=payload.session_id,
            english_reply=result.get("english_reply", ""),
            translated_reply=result.get("translated_reply", ""),
            register_explanation=result.get("register_explanation", ""),
            model_used=model_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart reply engine error: {str(e)}")