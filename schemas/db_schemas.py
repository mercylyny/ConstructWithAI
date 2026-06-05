from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class WallBase(BaseModel):
    wall_id: str
    length_m: float
    height_m: float
    thickness_mm: float
    openings_area_m2: Optional[float] = 0.0
    wall_type: Optional[str] = "UNKNOWN"
    classification_confidence: Optional[float] = 0.0
    reasoning: Optional[str] = ""

class WallCreate(WallBase):
    pass

class Wall(WallBase):
    id: int
    project_id: int
    model_config = ConfigDict(from_attributes=True)

class EstimationPhaseSchema(BaseModel):
    id: int
    phase_name: str
    cost: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EstimationBase(BaseModel):
    total_bricks: int = 0
    total_mortar_volume: float = 0.0
    total_cost: float = 0.0
    grand_total: float = 0.0
    boq_excel_path: Optional[str] = None
    boq_pdf_path: Optional[str] = None

class EstimationCreate(EstimationBase):
    pass

class Estimation(EstimationBase):
    id: int
    project_id: int
    created_at: datetime
    phases: List[EstimationPhaseSchema] = []
    model_config = ConfigDict(from_attributes=True)

class BuildingSummarySchema(BaseModel):
    id: int
    rooms: int = 0
    bedrooms: int = 0
    bathrooms: int = 0
    kitchens: int = 0
    walls: int = 0
    doors: int = 0
    windows: int = 0
    columns: int = 0
    beams: int = 0
    confidence: float = 0.0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    filename: str
    scale: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    walls: List[Wall] = []
    estimations: List[Estimation] = []
    building_summaries: List[BuildingSummarySchema] = []
    model_config = ConfigDict(from_attributes=True)
