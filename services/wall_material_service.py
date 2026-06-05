from typing import List, Dict, Any
import math
from schemas.materials import WallSegment, WallMaterialResult, DetailedMaterialResponse, ProjectMaterialSummary

def estimate_wall_materials(walls: List[WallSegment]) -> DetailedMaterialResponse:
    """
    Detailed wall material estimation service.
    
    Assumptions:
    - Brick Size: 230mm x 75mm x 115mm
    - Mortar Thickness: 10mm
    - Coverage: 60 bricks per m2 (Standard for single-leaf/115mm or normalized)
    - Mortar Vol: 0.23 m3 per 1000 bricks
    - Walls are assumed to be multiples of 115mm width for brick count scaling.
      (If thickness is 230mm, brick count doubles).
    
    Formula:
    Net Area = (L * H) - Openings
    Bricks = Net Area * 60 * (Thickness_mm / 115)
    Mortar = (Bricks / 1000) * 0.23
    """
    
    wall_results = []
    
    total_bricks = 0
    total_mortar = 0.0
    
    # Constants
    BASE_COVERAGE_PER_M2 = 60  # Bricks per m2 for standard leaf
    BASE_THICKNESS_MM = 115    # Width of standard brick
    MORTAR_PER_1000_BRICKS = 0.23
    
    for wall in walls:
        # 1. Net Area
        gross_area = wall.length_m * wall.height_m
        net_area = max(0.0, gross_area - wall.openings_area_m2)
        
        # 2. Determine Thickness Factor
        # If thickness is close to 115, factor 1. If 230, factor 2.
        # We'll use continuous scaling to handle variations (e.g. 150mm), 
        # but logically it should be steps. For estimation, continuous is safe or rounding.
        # User specified "Brick wall coverage: 60 bricks per square meter".
        # This is ambiguous for thick walls. I will assume it implies scaling by thickness ratio vs standard leaf.
        thickness_factor = wall.thickness_mm / BASE_THICKNESS_MM
        # Clamp minimum factor to 0.5 (unlikely to have thinner than half-brick on face?)
        # Actually 75mm partitions exists (brick on edge). 75/115 = 0.65.
        
        # 3. Brick Count
        bricks_count_float = net_area * BASE_COVERAGE_PER_M2 * thickness_factor
        bricks_count = math.ceil(bricks_count_float)
        
        # 4. Mortar Volume
        mortar_vol = (bricks_count / 1000.0) * MORTAR_PER_1000_BRICKS
        mortar_vol = round(mortar_vol, 4)
        
        # Add to list
        wall_results.append(WallMaterialResult(
            wall_id=wall.wall_id,
            net_area_m2=round(net_area, 2),
            total_bricks=bricks_count,
            mortar_volume_m3=mortar_vol
        ))
        
        # Add to totals
        total_bricks += bricks_count
        total_mortar += mortar_vol
        
    return DetailedMaterialResponse(
        walls=wall_results,
        project_totals=ProjectMaterialSummary(
            total_bricks_count=total_bricks,
            total_mortar_volume_m3=round(total_mortar, 3)
        )
    )
