from pydantic import BaseModel
from typing import List, Optional

class AIInterpretOCRRequest(BaseModel):
    filename: str

class DetectedElements(BaseModel):
    rooms: int = 0
    bedrooms: int = 0
    bathrooms: int = 0
    kitchens: int = 0
    living_rooms: int = 0
    dining_rooms: int = 0
    stores: int = 0
    walls: int = 0
    doors: int = 0
    windows: int = 0
    columns: int = 0
    beams: int = 0
    other_elements: int = 0

class InterpretedWall(BaseModel):
    label: str
    length_m: float

class InterpretedData(BaseModel):
    walls: List[InterpretedWall]
    assumed_wall_height_m: Optional[float] = None

class AIInterpretOCRResponse(BaseModel):
    filename: str
    interpreted_data: InterpretedData
    detected_elements: DetectedElements
    confidence: str
    message: str
