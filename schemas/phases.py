from pydantic import BaseModel
from typing import List, Optional


class PhaseMaterialItem(BaseModel):
    item: str
    quantity: float
    unit: str
    unit_rate: float
    total_cost: float
    notes: Optional[str] = None


class PhaseGroup(BaseModel):
    phase_name: str
    materials: List[PhaseMaterialItem]
    phase_cost: float
    comments: Optional[str] = None


class PhaseEstimationResponse(BaseModel):
    filename: str
    phases: List[PhaseGroup]
    total_project_cost: float
    summary: str
    detected_phases: Optional[List[str]] = None
