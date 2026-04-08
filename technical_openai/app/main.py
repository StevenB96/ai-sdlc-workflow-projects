import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .provider import triage_issue
from .schemas import TriageRequest, TriageResponse

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
)

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Incident Triage API", version="0.1.0")


@app.get("/")
def root():
    """
    Root endpoint returning basic API info and available paths.
    """
    return {
        "message": "AI Incident Triage API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    """
    Health check endpoint. Returns 'ok' if the API is running.
    """
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
def triage(req: TriageRequest):
    """
    Accepts an incident triage request and returns predicted severity
    and probable component. Logs success or failure.
    """
    try:
        result = triage_issue(req)
        validated = TriageResponse(**result)

        logger.info(
            'triage_success title="%s" severity="%s" component="%s"',
            req.title,
            validated.severity,
            validated.probable_component,
        )
        return validated
    except Exception as err:
        logger.exception("triage_failed")
        raise HTTPException(
            status_code=500, detail=f"triage failed: {err}") from err
