from pydantic import BaseModel
from typing import List, Dict, Optional

# Import PhaseMaterialItem to include detailed materials per phase
from schemas.phases import PhaseMaterialItem

class WallQuantity(BaseModel):
    label: str
    length_m: float
    height_m: float
    thickness_m: float = 0.2
    area_sqm: float
    volume_cum: float
    data_source: str = "OCR" # MANUAL, OCR, HYBRID, INFERRED
    confidence_weight: float = 0.0

class EstimationTotals(BaseModel):
    total_wall_area_sqm: float
    total_wall_volume_cum: float

class WallEstimationResponse(BaseModel):
    filename: str
    walls: List[WallQuantity]
    totals: EstimationTotals
    message: str

class BuildingSummary(BaseModel):
    rooms: int = 0
    bedrooms: int = 0
    bathrooms: int = 0
    kitchens: int = 0
    walls: int = 0
    doors: int = 0
    windows: int = 0
    columns: int = 0
    beams: int = 0
    stairs: int = 0
    confidence: float = 0.0

class PlanAnalysisResult(BaseModel):
    filename: str
    status: str
    summary: BuildingSummary
    extracted_text: str = ""
    boq_excel_path: str = None
    qs_report_path: str = None
    message: str = ""

class EstimationStageTotal(BaseModel):
    phase_name: str
    cost: float
    materials: List[PhaseMaterialItem] = []

class EstimationRequest(BaseModel):
    filename: Optional[str] = None
    summary: BuildingSummary
    manual_mode: bool = False
    manual_walls: Optional[List[WallQuantity]] = None
    project_id: Optional[int] = None

class EstimationResult(BaseModel):
    status: str
    message: Optional[str] = None
    stages: Optional[List[EstimationStageTotal]] = None
    grand_total: Optional[float] = None
    boq_excel_path: Optional[str] = None
    boq_pdf_path: Optional[str] = None
    qs_report_path: Optional[str] = None

class PipelineExecutionResult(BaseModel):
    status: str
    failed_step: Optional[str] = None
    failure_reason: Optional[str] = None
    wall_count: int = 0
    total_cost: float = 0.0
    extracted_text: str = ""
    intervention_needed: bool = False
    missing_critical_data: List[str] = []
    confidence_breakdown: Dict[str, float] = {}
    readiness_status: str = "NOT_READY"
    readiness_score: float = 0.0
    boq_excel_path: Optional[str] = None
    boq_pdf_path: Optional[str] = None
    qs_report_path: Optional[str] = None
    narrative_report: str = ""
