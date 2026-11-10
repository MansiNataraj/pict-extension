import logging
import time
from fastapi import APIRouter, HTTPException
from app.models import (
    CrtQuestion, CrtQuestionsRequest, CrtQuestionsResponse,
    CrtNote, CrtVariant, CrtTranslateRequest, CrtTranslateResponse,
)
from app.prompts import get_crt_questions_prompt, get_crt_translate_prompt
from app.chains import execute_llm_chain
from app.logging_config import preview
from config import SUPPORTED_LANGUAGES

log = logging.getLogger("pitc.crt")
router = APIRouter(prefix="/crt", tags=["CRT Translate"])

ALL_LANGS = {
    **SUPPORTED_LANGUAGES,
    "en": {"name": "English", "t_v_system": "Modal politeness (would/could/please)"},
}
MAX_TEXT_CHARS = 1500
VALID_CODES = {"C1", "C2", "C3", "C4", "C5"}


def _resolve_langs(source: str, target: str):
    src = (source or "auto").strip().lower()
    tgt = (target or "").strip().lower()
    if tgt not in ALL_LANGS:
        raise HTTPException(status_code=400, detail=f"Unsupported target language '{target}'.")
    if src != "auto" and src not in ALL_LANGS:
        raise HTTPException(status_code=400, detail=f"Unsupported source language '{source}'.")
    if src == tgt:
        raise HTTPException(status_code=400, detail="Source and target languages must be different.")
    src_name = "the source language (auto-detect it)" if src == "auto" else ALL_LANGS[src]["name"]
    return src, tgt, src_name


def _check_text(text: str) -> str:
    text = (text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is empty.")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail=f"Text is too long (max {MAX_TEXT_CHARS} characters).")
    return text


@router.post("/questions", response_model=CrtQuestionsResponse)
async def crt_questions(req: CrtQuestionsRequest):
    text = _check_text(req.text)
    src, tgt, src_name = _resolve_langs(req.source_language, req.target_language)
    log.info("questions: %s->%s chars=%d text=%r", src, tgt, len(text), preview(text))

    prompt = get_crt_questions_prompt(text, src_name, ALL_LANGS[tgt]["name"], ALL_LANGS[tgt]["t_v_system"])
    started = time.perf_counter()
    try:
        result, model_used = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)
    except Exception as e:
        log.error("questions: LLM chain failed: %s", e)
        raise HTTPException(status_code=500, detail=f"CRT questions failed: {e}")

    questions = []
    for i, q in enumerate(result.get("questions") or [], start=1):
        try:
            code = str(q.get("crt_code", "")).upper()
            options = [str(o) for o in (q.get("options") or []) if str(o).strip()]
            if code not in VALID_CODES or not q.get("question") or len(options) < 2:
                log.warning("questions: dropped malformed question #%d: %r", i, q)
                continue
            questions.append(CrtQuestion(id=str(q.get("id") or f"q{i}"), crt_code=code,
                                         question=str(q["question"]), options=options[:4]))
        except Exception as err:
            log.warning("questions: dropped unparsable question #%d (%s): %r", i, err, q)
    questions = questions[:2]

    log.info("questions: returned %d (%s) model=%s in %.0f ms",
             len(questions), ",".join(q.crt_code for q in questions) or "none",
             model_used, (time.perf_counter() - started) * 1000)
    return CrtQuestionsResponse(questions=questions, model_used=model_used)


@router.post("/translate", response_model=CrtTranslateResponse)
async def crt_translate(req: CrtTranslateRequest):
    text = _check_text(req.text)
    src, tgt, src_name = _resolve_langs(req.source_language, req.target_language)
    log.info("translate: %s->%s chars=%d answers=%d text=%r",
             src, tgt, len(text), len(req.answers), preview(text))
    for a in req.answers:
        log.info("translate: answer [%s] %s -> %s", a.crt_code, a.question, a.answer)

    prompt = get_crt_translate_prompt(text, src_name, ALL_LANGS[tgt]["name"],
                                      ALL_LANGS[tgt]["t_v_system"], req.answers)
    started = time.perf_counter()
    try:
        result, model_used = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)
    except Exception as e:
        log.error("translate: LLM chain failed: %s", e)
        raise HTTPException(status_code=500, detail=f"CRT translation failed: {e}")

    translated = str(result.get("translated_text") or "").strip()
    if not translated:
        log.error("translate: model returned no translated_text. raw keys=%s", list(result.keys()))
        raise HTTPException(status_code=502, detail="The model returned an empty translation. Try again.")

    notes = []
    for n in result.get("crt_applied") or []:
        if isinstance(n, dict) and n.get("note"):
            notes.append(CrtNote(code=str(n.get("code", "")).upper(), note=str(n["note"])))

    variants = []
    for v in result.get("variants") or []:
        if isinstance(v, dict) and v.get("text"):
            variants.append(CrtVariant(label=str(v.get("register", "")), text=str(v["text"]),
                                       nuance=str(v.get("nuance", ""))))

    log.info("translate: ok model=%s notes=%d variants=%d in %.0f ms",
             model_used, len(notes), len(variants), (time.perf_counter() - started) * 1000)
    return CrtTranslateResponse(
        translated_text=translated,
        register_used=str(result.get("register_used") or "N/A"),
        crt_applied=notes,
        variants=variants,
        cultural_notes=str(result.get("cultural_notes") or ""),
        model_used=model_used,
    )
