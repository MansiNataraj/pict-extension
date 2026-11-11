"""PITC backend entry point. Run: uvicorn main:app --port 8000"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.logging_config import LOG_FILE, setup_logging
from app.middleware import log_requests
from app.routers import ALL_ROUTERS
from config import CLOUD_API_KEY, CLOUD_MODEL_NAME, LOCAL_MODEL_NAME, OLLAMA_BASE_URL

setup_logging()
log = logging.getLogger("pitc.api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    log.info("PITC backend starting. Gemini key set: %s | cloud model: %s | local model: %s @ %s",
             bool(CLOUD_API_KEY), CLOUD_MODEL_NAME, LOCAL_MODEL_NAME, OLLAMA_BASE_URL)
    if not CLOUD_API_KEY:
        log.warning("GEMINI_API_KEY is empty. Create backend/.env from .env.example and restart.")
    log.info("Logging to %s", LOG_FILE)
    yield


app = FastAPI(title="PITC - Proactive Intelligent Translation Coach", version="2.0.0", lifespan=lifespan)

# Open CORS is fine here: the server is meant to run on the user's own machine only.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.middleware("http")(log_requests)

for router in ALL_ROUTERS:
    app.include_router(router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "PITC Backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
