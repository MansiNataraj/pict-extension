from fastapi import APIRouter, HTTPException
from app.models import ChatReplyRequest, ChatReplyResponse
from app.prompts import get_chat_reply_prompt
from app.chains import execute_llm_chain
from config import SUPPORTED_LANGUAGES

router = APIRouter(prefix="/chat-reply", tags=["Chat Reply"])


@router.post("", response_model=ChatReplyResponse)
@router.post("/", response_model=ChatReplyResponse)
async def chat_reply(req: ChatReplyRequest):
    lang = SUPPORTED_LANGUAGES.get(req.language_code)
    if not lang:
        raise HTTPException(status_code=400, detail="Unsupported language code")
    if not req.conversation_history:
        raise HTTPException(status_code=400, detail="conversation_history is empty")

    prompt = get_chat_reply_prompt(lang["name"], req.contact_name, req.contact_role, req.conversation_history)
    try:
        result, model = await execute_llm_chain(prompt, temperature=0.7, provider=req.provider)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"No AI provider available (set GEMINI_API_KEY in backend/.env or start Ollama): {e}",
        )

    reply = (result.get("reply") or "").strip()
    if not reply:
        raise HTTPException(status_code=502, detail="Model returned an empty reply")
    return ChatReplyResponse(speaker=req.contact_name, reply=reply, model_used=model)
