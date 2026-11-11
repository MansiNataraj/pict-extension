"""Legacy web-app endpoint: audit a whole conversation thread for cultural friction."""
from fastapi import APIRouter, HTTPException
from app.chains import execute_llm_chain
from app.models import ThreadAnalyseRequest, ThreadAnalyseResponse
from app.prompts import get_thread_analysis_prompt
from config import SUPPORTED_LANGUAGES

router = APIRouter(prefix="/analyse", tags=["Thread Analyser"])


@router.post("", response_model=ThreadAnalyseResponse)
@router.post("/", response_model=ThreadAnalyseResponse, include_in_schema=False)
async def analyse_thread(req: ThreadAnalyseRequest):
    lang = SUPPORTED_LANGUAGES.get(req.language_code)
    if not lang:
        raise HTTPException(status_code=400, detail="Unsupported language code")

    prompt = get_thread_analysis_prompt(lang["name"], req.thread)
    try:
        result, model = await execute_llm_chain(prompt, temperature=0.2, provider=req.provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thread analysis failed: {e}")

    return ThreadAnalyseResponse(
        session_id=req.session_id,
        health_score=_as_int(result.get("health_score"), 85),
        crt_violations=[str(v) for v in (result.get("crt_violations") or [])],
        root_cause=result.get("root_cause", "No severe relational friction detected."),
        remediation_advice=result.get("remediation_advice", "Maintain current honorific register."),
        model_used=model,
    )


def _as_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
