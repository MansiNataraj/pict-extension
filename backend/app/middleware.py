"""HTTP middleware: one log line per request, plus unhandled-error logging."""
import logging
import time
from fastapi import Request

log = logging.getLogger("pitc.api")


async def log_requests(request: Request, call_next):
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
