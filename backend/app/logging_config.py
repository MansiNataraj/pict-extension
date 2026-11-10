"""Central logging setup. Logs go to the console and to backend/pitc.log (rotating)."""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pitc.log")
_FORMAT = "%(asctime)s %(levelname)-7s [%(name)s] %(message)s"


def setup_logging() -> None:
    root = logging.getLogger("pitc")
    if root.handlers:  # already configured (uvicorn --reload re-imports)
        return
    level = os.getenv("PITC_LOG_LEVEL", "INFO").upper()
    root.setLevel(level)
    root.propagate = False

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(_FORMAT))
    root.addHandler(console)

    try:
        fh = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setFormatter(logging.Formatter(_FORMAT))
        root.addHandler(fh)
    except OSError as err:
        root.warning("Could not open log file %s: %s", LOG_FILE, err)


def preview(text: str, limit: int = 60) -> str:
    """Short single-line preview of user text for logs (full text is not logged)."""
    flat = " ".join((text or "").split())
    return flat if len(flat) <= limit else flat[:limit] + "..."
