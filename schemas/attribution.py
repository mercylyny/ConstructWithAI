from pydantic import BaseModel
from typing import List, Optional

class EvidenceSource(BaseModel):
    type: str  # image | text | rule
    reference: str

class AttributedValue(BaseModel):
    name: str
    value: float
    unit: str
    source: str  # OCR | HUMAN | ASSUMPTION | LEARNED_RULE
    confidence: float
    evidence: List[EvidenceSource]
    risk_flag: str  # LOW | MEDIUM | HIGH

class AttributionResponse(BaseModel):
    attributed_values: List[AttributedValue]
    engineering_commentary: str
