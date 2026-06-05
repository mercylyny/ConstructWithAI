from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class FailureItem(BaseModel):
    stage: str
    category: str
    root_cause: str
    severity: str
    human_action_required: bool
    recommended_fix: str

class FailureAnalysisRequest(BaseModel):
    pipeline_logs: List[str]
    ocr_output: str
    confidence_scores: Dict[str, float]
    missing_values: List[str]
    evidence_results: Dict[str, Any]

class FailureAnalysisResponse(BaseModel):
    failures: List[FailureItem]
    overall_system_health: str
    engineering_summary: str
