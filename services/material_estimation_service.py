import math
from typing import List
from schemas.estimation import WallQuantity
from schemas.materials import WallMaterialEstimate, BuildingMaterialSummary, MaterialEstimationResponse
from services.estimation_service import calculate_wall_quantities

# Material Constants
BLOCKS_PER_CUBIC_METER = 12.5
BRICKS_PER_CUBIC_METER = 500
BLOCK_WASTAGE_FACTOR = 1.10  # 10% wastage
BRICK_WASTAGE_FACTOR = 1.15  # 15% wastage

def estimate_blocks_from_walls(walls: List[WallQuantity]) -> List[WallMaterialEstimate]:
    """
    Calculate block quantities for each wall based on volume.
    Formula: blocks = volume_m3 * blocks_per_m3
    """
    estimates = []
    
    for wall in walls:
        # Base calculation
        blocks_base = wall.volume_cum * BLOCKS_PER_CUBIC_METER
        blocks_required = math.ceil(blocks_base)
        
        # Apply wastage
        blocks_with_wastage = math.ceil(blocks_base * BLOCK_WASTAGE_FACTOR)
        
        # For bricks, we calculate but they're not the primary material for this endpoint
        bricks_base = wall.volume_cum * BRICKS_PER_CUBIC_METER
        bricks_required = math.ceil(bricks_base)
        bricks_with_wastage = math.ceil(bricks_base * BRICK_WASTAGE_FACTOR)
        
        estimates.append(WallMaterialEstimate(
            wall_label=wall.label,
            volume_m3=wall.volume_cum,
            blocks_required=blocks_required,
            bricks_required=bricks_required,
            blocks_with_wastage=blocks_with_wastage,
            bricks_with_wastage=bricks_with_wastage
        ))
    
    return estimates

def estimate_bricks_from_walls(walls: List[WallQuantity]) -> List[WallMaterialEstimate]:
    """
    Calculate brick quantities for each wall based on volume.
    Formula: bricks = volume_m3 * bricks_per_m3
    """
    # Reuse the same calculation logic
    return estimate_blocks_from_walls(walls)

def calculate_material_estimation(filename: str, material_type: str) -> MaterialEstimationResponse:
    """
    Main function to calculate material estimates.
    Reuses Phase 7.5 wall quantity estimation.
    """
    # Step 1: Get wall quantities from Phase 7.5
    wall_estimation = calculate_wall_quantities(filename)
    
    if wall_estimation is None:
        return None
    
    # Step 2: Calculate material estimates
    if material_type == "blocks":
        wall_materials = estimate_blocks_from_walls(wall_estimation.walls)
    elif material_type == "bricks":
        wall_materials = estimate_bricks_from_walls(wall_estimation.walls)
    else:
        raise ValueError(f"Invalid material_type: {material_type}")
    
    # Step 3: Calculate totals
    total_volume = sum(w.volume_m3 for w in wall_materials)
    total_blocks = sum(w.blocks_required for w in wall_materials)
    total_bricks = sum(w.bricks_required for w in wall_materials)
    total_blocks_wastage = sum(w.blocks_with_wastage for w in wall_materials)
    total_bricks_wastage = sum(w.bricks_with_wastage for w in wall_materials)
    
    summary = BuildingMaterialSummary(
        total_walls=len(wall_materials),
        total_volume_m3=round(total_volume, 2),
        total_blocks=total_blocks,
        total_bricks=total_bricks,
        total_blocks_with_wastage=total_blocks_wastage,
        total_bricks_with_wastage=total_bricks_wastage
    )
    
    # Step 4: Build response
    return MaterialEstimationResponse(
        filename=filename,
        material_type=material_type,
        walls=wall_materials,
        summary=summary,
        message=f"{material_type.capitalize()} estimation completed successfully"
    )
