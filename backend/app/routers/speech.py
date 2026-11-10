from fastapi import APIRouter, HTTPException
from app.models import SpeechTranslateRequest, SpeechTranslateResponse
from app.prompts import get_speech_translate_prompt
from app.chains import execute_llm_chain
from config import SUPPORTED_LANGUAGES

router = APIRouter(prefix="/speech-translate", tags=["Speech Translation"])

ALL_SPEECH_LANGS = {
    **SUPPORTED_LANGUAGES,
    "en": {"name": "English", "t_v_system": "Modal politeness (would/could/please)"}
}

@router.post("", response_model=SpeechTranslateResponse)
@router.post("/", response_model=SpeechTranslateResponse)
async def translate_speech(req: SpeechTranslateRequest):
    src = req.source_language.strip().lower()
    tgt = req.target_language.strip().lower()

    if src not in ALL_SPEECH_LANGS or tgt not in ALL_SPEECH_LANGS:
        raise HTTPException(status_code=400, detail="Unsupported language code.")
    if src == tgt:
        raise HTTPException(status_code=400, detail="Source and Target languages must be different.")

    prompt = get_speech_translate_prompt(
        text=req.audio_text,
        src_lang=ALL_SPEECH_LANGS[src]["name"],
        tgt_lang=ALL_SPEECH_LANGS[tgt]["name"],
        tone=req.tone
    )

    try:
        result, model_used = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)
        return SpeechTranslateResponse(
            session_id=req.session_id,
            original_text=req.audio_text,
            translated_text=result.get("translated_text", req.audio_text),
            source_language=src,
            target_language=tgt,
            selected_tone=req.tone,
            t_v_pronoun_used=result.get("t_v_pronoun_used", "N/A"),
            cultural_notes=result.get("cultural_notes", "Calibrated for pragmatic tone."),
            model_used=model_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech translation failed: {str(e)}")