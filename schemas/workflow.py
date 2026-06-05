from typing import List, Dict, Any
from pydantic import BaseModel

class WorkflowStep(BaseModel):
    step: int
    action: str
    endpoint: str
    required: bool

class WorkflowOrchestratorRequest(BaseModel):
    confidence_score: float
    readiness_status: str
    failures: List[Dict[str, Any]]
    available_data: Dict[str, bool]

class WorkflowOrchestratorResponse(BaseModel):
    recommended_mode: str
    steps: List[WorkflowStep]
    warnings: List[str]
    next_action: str
