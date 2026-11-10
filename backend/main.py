from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import speech, chat_reply
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
from config import SUPPORTED_LANGUAGES

app = FastAPI(
    title="PITC - Proactive Intelligent Translation Coach",
    version="2.0.0"
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