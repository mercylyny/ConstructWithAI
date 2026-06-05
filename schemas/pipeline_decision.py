from pydantic import BaseModel
from typing import List, Dict

class PipelineActions(BaseModel):
    estimate_from_plan: bool
    estimate_from_ocr: bool
    manual_input_required: bool
    manual_verification_required: bool
    materials_detailed: bool
    cost_estimation: bool
    boq_reports: bool

class PipelineDecision(BaseModel):
    path: str # FULL_AUTOMATION | HYBRID | MANUAL_FIRST
    confidence_level: str # LOW | MEDIUM | HIGH
    actions: PipelineActions
    risk_flags: List[str]
    reasoning: str

class PipelineDecisionResponse(BaseModel):
    pipeline_decision: PipelineDecision
