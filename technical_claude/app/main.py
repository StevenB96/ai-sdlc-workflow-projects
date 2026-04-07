import logging
import os
from fastapi import FastAPI, HTTPException
from .schemas import TriageRequest, TriageResponse
from .provider import triage_issue

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
)

app = FastAPI(title="AI Incident Triage API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
def triage(req: TriageRequest):
    try:
        result = triage_issue(req)
        validated = TriageResponse(**result)
        logging.info(
            'triage_success title="%s" severity="%s" component="%s"',
            req.title,
            validated.severity,
            validated.probable_component,
        )
        return validated
    except Exception as err:
        logging.exception("triage_failed")
        raise HTTPException(status_code=500, detail=f"triage failed: {err}")
