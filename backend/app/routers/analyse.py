from fastapi import APIRouter, HTTPException
from app.models import ThreadAnalyseRequest, ThreadAnalyseResponse
from app.prompts import get_analyse_prompt
from app.chains import execute_llm_chain
from config import SUPPORTED_LANGUAGES

router = APIRouter(prefix="/analyse", tags=["Thread Analyser"])

@router.post("", response_model=ThreadAnalyseResponse)
@router.post("/", response_model=ThreadAnalyseResponse)
async def analyse_conversation_thread(payload: ThreadAnalyseRequest):
    lang_info = SUPPORTED_LANGUAGES.get(payload.language_code)
    if not lang_info:
        raise HTTPException(status_code=400, detail="Unsupported language code")

    thread_lines = [f"[{i}] {msg.speaker}: {msg.message}" for i, msg in enumerate(payload.thread)]
    thread_text = "\n".join(thread_lines)

    prompt = get_analyse_prompt(
        language_name=lang_info["name"],
        t_v_info=lang_info["t_v_system"],
        thread_text=thread_text
    )

    try:
        result, model_used = await execute_llm_chain(
            prompt, 
            temperature=0.1, 
            provider=payload.provider
        )
        return ThreadAnalyseResponse(
            session_id=payload.session_id,
            health_score=result.get("health_score", "Low"),
            health_explanation=result.get("health_explanation", "Conversation flow evaluated."),
            riskiest_message_index=int(result.get("riskiest_message_index", 0)),
            crt_category=result.get("crt_category", "None"),
            crt_explanation=result.get("crt_explanation", "No major friction detected."),
            recommendation=result.get("recommendation", "Continue respectful conversation."),
            model_used=model_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis engine error: {str(e)}")