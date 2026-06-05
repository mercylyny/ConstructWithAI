from pydantic import BaseModel
from typing import List

class WallMaterialEstimate(BaseModel):
    """Material estimate for a single wall"""
    wall_label: str
    volume_m3: float
    blocks_required: int
    bricks_required: int
    blocks_with_wastage: int
    bricks_with_wastage: int

class BuildingMaterialSummary(BaseModel):
    """Aggregated material summary for the entire building"""
    total_walls: int
    total_volume_m3: float
    total_blocks: int
    total_bricks: int
    total_blocks_with_wastage: int
    total_bricks_with_wastage: int

class MaterialEstimationResponse(BaseModel):
    """Response for material estimation endpoints"""
    filename: str
    material_type: str  # "blocks" or "bricks"
    walls: List[WallMaterialEstimate]
    summary: BuildingMaterialSummary
    message: str

class WallSegment(BaseModel):
    """Detailed wall segment input for material estimation"""
    wall_id: str
    length_m: float
    height_m: float
    thickness_mm: float
    openings_area_m2: float = 0.0

class WallMaterialResult(BaseModel):
    """Detailed material result for a single wall"""
    wall_id: str
    net_area_m2: float
    total_bricks: int
    mortar_volume_m3: float

class ProjectMaterialSummary(BaseModel):
    """Aggregate totals for the project"""
    total_bricks_count: int
    total_mortar_volume_m3: float

class DetailedMaterialResponse(BaseModel):
    """Response for detailed material estimation"""
    walls: List[WallMaterialResult]
    project_totals: ProjectMaterialSummary
