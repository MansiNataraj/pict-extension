import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.logging_config import setup_logging, LOG_FILE
from app.routers import speech, chat_reply, crt
from app.models import (
    ThreadAnalyseRequest, ThreadAnalyseResponse,
    CoachRequest, CoachResponse,
    ReplyRequest, ReplyResponse
)
from app.prompts import (
    get_thread_analysis_prompt,
    get_coaching_prompt,
    get_reply_ghostwriter_prompt
)
from app.chains import execute_llm_chain
from config import SUPPORTED_LANGUAGES, CLOUD_API_KEY, CLOUD_MODEL_NAME, LOCAL_MODEL_NAME, OLLAMA_BASE_URL

setup_logging()
log = logging.getLogger("pitc.api")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    _log_startup()
    yield


app = FastAPI(
    title="PITC - Proactive Intelligent Translation Coach",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Speech Translation router
app.include_router(speech.router)
app.include_router(chat_reply.router)
app.include_router(crt.router)

def _log_startup():
    log.info("PITC backend starting. Gemini key set: %s | cloud model: %s | local model: %s @ %s",
             bool(CLOUD_API_KEY), CLOUD_MODEL_NAME, LOCAL_MODEL_NAME, OLLAMA_BASE_URL)
    if not CLOUD_API_KEY:
        log.warning("GEMINI_API_KEY is empty. Create backend/.env from .env.example and restart.")
    log.info("Logging to %s", LOG_FILE)


@app.middleware("http")
async def _log_requests(request: Request, call_next):
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        log.exception("%s %s -> unhandled error", request.method, request.url.path)
        raise
    if request.url.path != "/health":
        log.info("%s %s -> %d (%.0f ms)", request.method, request.url.path,
                 response.status_code, (time.perf_counter() - started) * 1000)
    return response


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "PITC Backend"}

@app.post("/analyse", response_model=ThreadAnalyseResponse)
async def analyse_thread(req: ThreadAnalyseRequest):
    lang_name = SUPPORTED_LANGUAGES.get(req.language_code, {}).get("name", "Hindi")
    prompt = get_thread_analysis_prompt(lang_name, req.thread)
    result, model = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)

    return ThreadAnalyseResponse(
        session_id=req.session_id,
        health_score=result.get("health_score", 85),
        crt_violations=result.get("crt_violations", []),
        root_cause=result.get("root_cause", "No severe relational friction detected."),
        remediation_advice=result.get("remediation_advice", "Maintain current honorific register."),
        model_used=model
    )

@app.post("/coach", response_model=CoachResponse)
async def coach_draft(req: CoachRequest):
    lang_name = SUPPORTED_LANGUAGES.get(req.language_code, {}).get("name", "Hindi")
    prompt = get_coaching_prompt(lang_name, req.draft_message, req.recipient_role)
    result, model = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)

    return CoachResponse(
        is_risky=result.get("is_risky", False),
        risk_level=result.get("risk_level", "green"),
        crt_code=result.get("crt_code"),
        warning_message=result.get("warning_message"),
        clarification_question=result.get("clarification_question"),
        variants=result.get("variants"),
        predicted_reactions=result.get("predicted_reactions"),
        model_used=model
    )

@app.post("/reply", response_model=ReplyResponse)
async def suggest_reply(req: ReplyRequest):
    lang_name = SUPPORTED_LANGUAGES.get(req.language_code, {}).get("name", "Hindi")
    prompt = get_reply_ghostwriter_prompt(lang_name, req.conversation_history, req.goal)
    result, model = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)

    return ReplyResponse(
        suggested_reply=result.get("suggested_reply", ""),
        diplomatic_rationale=result.get("diplomatic_rationale", "Aligned with diplomatic goals."),
        model_used=model
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)