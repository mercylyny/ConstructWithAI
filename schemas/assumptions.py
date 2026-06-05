from typing import List, Dict, Any
from pydantic import BaseModel

class AssumptionItem(BaseModel):
    name: str
    value: float
    unit: str
    source: str
    reason: str
    confidence: str
    override_allowed: bool

class AssumptionsRequest(BaseModel):
    material_results: Dict[str, Any]
    cost_results: Dict[str, Any]
    known_constants: Dict[str, Any]
    calculation_defaults: Dict[str, Any]

class AssumptionsResponse(BaseModel):
    assumptions: List[AssumptionItem]
    engineering_summary: str
