from pydantic import BaseModel
from typing import List

class WallSegment(BaseModel):
    segment_id: str
    parent_wall_id: str
    segment_length_m: float
    segment_height_m: float
    segment_net_area_m2: float
    normalized_thickness_mm: int
    original_thickness_mm: int
    segment_confidence: float
    review_flag: bool

class NormalizationResponse(BaseModel):
    wall_segments: List[WallSegment]
    segmentation_quality: str # HIGH | MEDIUM | LOW
