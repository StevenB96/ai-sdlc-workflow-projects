from typing import List, Literal
from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high", "critical"]
Component = Literal["frontend", "backend",
                    "database", "auth", "infra", "unknown"]


class TriageRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: str
    logs: str = ""
    changed_files: List[str] = Field(default_factory=list)
    service_name: str = "unknown"


class TriageResponse(BaseModel):
    severity: Severity
    probable_component: Component
    root_cause_hypothesis: str
    recommended_fix: str
    test_plan: List[str] = Field(default_factory=list)
    rollback_plan: str
    release_note: str
    confidence: float = Field(ge=0.0, le=1.0)
