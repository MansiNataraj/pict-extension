import json
import logging
import re
import time
from typing import Any, Dict, Tuple
import httpx
from openai import AsyncOpenAI
from config import (
    CLOUD_API_KEY,
    CLOUD_MODEL_NAME,
    OLLAMA_BASE_URL,
    LOCAL_MODEL_NAME,
    CLOUD_TIMEOUT_SECONDS
)

log = logging.getLogger("pitc.llm")

local_client = AsyncOpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama"
)

CLOUD_CANDIDATES = [
    CLOUD_MODEL_NAME,
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash"
]

def clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    if not raw_text or not raw_text.strip():
        return {}

    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    if cleaned.endswith("```"):
        cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]

    try:
        return json.loads(cleaned)
    except Exception:
        sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", cleaned)
        try:
            return json.loads(sanitized)
        except Exception as err:
            log.warning("JSON parse failed: %s | raw[:200]=%r", err, raw_text[:200])
            return {}

async def _call_gemini_direct(model: str, prompt: str, temperature: float) -> Dict[str, Any]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "x-goog-api-key": CLOUD_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json"
        }
    }

    async with httpx.AsyncClient(timeout=CLOUD_TIMEOUT_SECONDS) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            # Surface Google's reason (bad key, unknown model, quota) instead of a bare status.
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return clean_and_parse_json(raw_text)

async def _call_ollama(model: str, prompt: str, temperature: float) -> Dict[str, Any]:
    response = await local_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a specialized cross-cultural pragmatic linguistic engine. Return strictly raw JSON."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content or "{}"
    return clean_and_parse_json(content)

async def execute_llm_chain(
    prompt: str,
    temperature: float = 0.2,
    provider: str = "auto"
) -> Tuple[Dict[str, Any], str]:
    mode = (provider or "auto").lower()

    log.info("LLM request: provider=%s key_set=%s prompt_chars=%d", mode, bool(CLOUD_API_KEY), len(prompt))

    if mode in ("cloud", "auto"):
        if not CLOUD_API_KEY:
            log.warning("GEMINI_API_KEY is not set; skipping cloud models")
        else:
            tried = set()
            for model_name in CLOUD_CANDIDATES:
                if model_name in tried:
                    continue
                tried.add(model_name)
                started = time.perf_counter()
                try:
                    result = await _call_gemini_direct(model_name, prompt, temperature)
                    ms = (time.perf_counter() - started) * 1000
                    if result:
                        log.info("Cloud %s OK in %.0f ms", model_name, ms)
                        return result, f"Cloud ({model_name})"
                    log.warning("Cloud %s returned empty/unparsable JSON after %.0f ms", model_name, ms)
                except Exception as cloud_err:
                    log.warning("Cloud %s failed after %.0f ms: %s: %s", model_name,
                                (time.perf_counter() - started) * 1000,
                                type(cloud_err).__name__, cloud_err)

    log.info("Falling back to local Ollama (%s at %s)", LOCAL_MODEL_NAME, OLLAMA_BASE_URL)
    started = time.perf_counter()
    try:
        result = await _call_ollama(LOCAL_MODEL_NAME, prompt, temperature)
        log.info("Ollama OK in %.0f ms", (time.perf_counter() - started) * 1000)
        return result, f"Local ({LOCAL_MODEL_NAME})"
    except Exception as local_err:
        log.error("Ollama failed: %s: %s", type(local_err).__name__, local_err)
        if not CLOUD_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Create backend/.env from .env.example, "
                "add your key, and restart the backend."
            ) from local_err
        raise RuntimeError(
            "All AI providers failed. Check backend/pitc.log for the Gemini error "
            "(invalid key, unknown model name or quota) and that the key is valid."
        ) from local_err
