from pydantic import BaseModel
from typing import List

class Opening(BaseModel):
    opening_id: str
    wall_id: str
    opening_type: str # DOOR | WINDOW
    width_m: float
    height_m: float
    position_m: float # Offset from the start of the wall centerline
    opening_confidence: float
    reasoning: str

class OpeningDetectionResponse(BaseModel):
    openings: List[Opening]
    opening_detection_quality: str # HIGH | MEDIUM | LOW
