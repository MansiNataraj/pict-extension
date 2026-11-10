import json
import re
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
            print(f"[JSON Parse Error]: {err}")
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
        resp.raise_for_status()
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

    if mode in ("cloud", "auto") and CLOUD_API_KEY:
        for model_name in CLOUD_CANDIDATES:
            try:
                result = await _call_gemini_direct(model_name, prompt, temperature)
                if result:
                    return result, f"Cloud ({model_name})"
            except Exception as cloud_err:
                print(f"[Notice] Cloud ({model_name}) attempt failed: {cloud_err}")

    # Fallback to local Ollama
    print(f"[Notice] Running local Ollama fallback ({LOCAL_MODEL_NAME})...")
    try:
        result = await _call_ollama(LOCAL_MODEL_NAME, prompt, temperature)
        return result, f"Local ({LOCAL_MODEL_NAME})"
    except Exception as local_err:
        print(f"[Critical] Both Cloud and Ollama failed: {local_err}")
        raise local_err