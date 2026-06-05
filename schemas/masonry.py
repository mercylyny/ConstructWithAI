from pydantic import BaseModel
from typing import List

class ClassifiedMasonrySegment(BaseModel):
    segment_id: str
    masonry_type: str # BRICK | BLOCK
    masonry_role: str # PARTITION | LOAD_BEARING | STRUCTURAL
    confidence: float

class MasonryClassificationResponse(BaseModel):
    classified_segments: List[ClassifiedMasonrySegment]
    project_masonry_system: str # BRICK | BLOCK | HYBRID
