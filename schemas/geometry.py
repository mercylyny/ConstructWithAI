from pydantic import BaseModel
from typing import List

class GeometricWall(BaseModel):
    wall_id: str
    length_m: float
    thickness_mm: int
    confidence: float
    source: str = "geometry"

class GeometryExtractionResponse(BaseModel):
    walls: List[GeometricWall]
    detected_rooms: int
    scale_confidence: float
    geometry_quality: str
