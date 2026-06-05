from pydantic import BaseModel
from typing import List

class ClassifiedWall(BaseModel):
    wall_id: str
    length_m: float
    thickness_mm: int
    wall_type: str # EXTERNAL | INTERNAL | LOAD_BEARING | NON_LOAD_BEARING
    classification_confidence: float
    reasoning: str

class SemanticClassificationResponse(BaseModel):
    classified_walls: List[ClassifiedWall]
    overall_classification_quality: str # HIGH | MEDIUM | LOW
