from pydantic import BaseModel
from typing import List

class HumanInputRequirement(BaseModel):
    parameter: str
    unit: str
    reason: str

class InterventionAnalysis(BaseModel):
    intervention_required: bool
    required_inputs: List[HumanInputRequirement]
    automation_allowed: List[str]
    engineering_note: str

class InterventionAnalysisResponse(BaseModel):
    intervention_analysis: InterventionAnalysis
