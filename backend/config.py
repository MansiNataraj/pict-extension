import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Cloud Provider (Gemini direct REST)
CLOUD_BASE_URL: str = os.getenv("CLOUD_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/models")
CLOUD_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
CLOUD_MODEL_NAME: str = os.getenv("CLOUD_MODEL_NAME", "gemini-3.5-flash-lite")
CLOUD_TIMEOUT_SECONDS: float = float(os.getenv("CLOUD_TIMEOUT_SECONDS", "10.0"))

# Local Fallback Provider (Ollama)
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
LOCAL_MODEL_NAME: str = os.getenv("LOCAL_MODEL_NAME", "aya-expanse:8b")

SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "hi": {
        "name": "Hindi",
        "native": "हिन्दी",
        "script": "Devanagari",
        "direction": "ltr",
        "t_v_system": "Aap (formal) / Tum (semi-formal) / Tu (informal)"
    },
    "ta": {
        "name": "Tamil",
        "native": "தமிழ்",
        "script": "Tamil",
        "direction": "ltr",
        "t_v_system": "Neenga (formal) / Nee (informal)"
    },
    "kn": {
        "name": "Kannada",
        "native": "ಕನ್ನಡ",
        "script": "Kannada",
        "direction": "ltr",
        "t_v_system": "Neevu (formal) / Neenu (informal)"
    },
    "ar": {
        "name": "Arabic",
        "native": "العربية",
        "script": "Arabic",
        "direction": "rtl",
        "t_v_system": "Hadratak/Antum (formal) / Inta (colloquial)"
    }
}

CRT_TAXONOMY: Dict[str, str] = {
    "C1": "Register Mismatch - Inappropriate honorific or pronoun level",
    "C2": "Idiomatic Opacity - Non-literal metaphors or idioms",
    "C3": "Gendered Language - Inappropriate grammatical gender markings",
    "C4": "Hierarchy Violation - Inadequate deference to seniority",
    "C5": "Cultural/Religious Sensitivity - Insensitive phrasing or taboos"
}
