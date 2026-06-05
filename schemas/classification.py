from pydantic import BaseModel
from typing import List, Dict, Optional

class DrawingMetadata_Custom(BaseModel):
    drawing_title: str
    drawing_type: str
    status: str

class SuitabilityScore(BaseModel):
    suitability: str
    confidence_score: float
    engineering_readiness: str

class VisualCues(BaseModel):
    geometry: str
    dimensions: str
    scale: str
    annotations: str
    legibility: str

class InterventionTriggers(BaseModel):
    automation_blockers: str
    verification_required: List[str]

class PlanClassificationReport(BaseModel):
    metadata: DrawingMetadata_Custom
    analysis_parameters: SuitabilityScore
    visual_cues_detection: VisualCues
    suitability_drivers: List[str]
    intervention_triggers: InterventionTriggers
    automation_recommendation: str
