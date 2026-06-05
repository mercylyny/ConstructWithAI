from typing import Tuple
from schemas.ai import InterpretedData
from schemas.estimation import WallQuantity, EstimationTotals, WallEstimationResponse
from services.ai_interpreter import get_stored_ocr_text, interpret_text_rule_based

def calculate_wall_quantities(filename: str) -> WallEstimationResponse:
    """
    Loads interpreted OCR data and calculates physical quantities (Area, Volume).
    """
    # 1. Get the raw text (reusing existing logic)
    text = get_stored_ocr_text(filename)
    if not text:
        # Caller (router) should handle specific 404/error response based on None content if preferred,
        # or we can raise here. Let's return None to signal "not found".
        return None

    # 2. Get interpreted data (reusing existing logic)
    # Note: In a real DB app, we'd save this to DB in Phase 7.4. 
    # Here we re-run the rule-based parser on the stored text.
    interpreted_data, _ = interpret_text_rule_based(text)
    
    # 3. Calculate Quantities
    estimated_walls = []
    total_area = 0.0
    total_volume = 0.0
    
    # Defaults
    default_height = interpreted_data.assumed_wall_height_m if interpreted_data.assumed_wall_height_m else 3.0
    default_thickness = 0.2
    
    for wall in interpreted_data.walls:
        # Use wall-specific height if we had it (schema doesn't have it yet, assumes global)
        # So we use assumed global height.
        h = default_height
        l = wall.length_m
        t = default_thickness
        
        area = round(l * h, 2)
        volume = round(area * t, 2)
        
        estimated_walls.append(WallQuantity(
            label=wall.label,
            length_m=l,
            height_m=h,
            thickness_m=t,
            area_sqm=area,
            volume_cum=volume
        ))
        
        total_area += area
        total_volume += volume
        
    # 4. Construct Response
    return WallEstimationResponse(
        filename=filename,
        walls=estimated_walls,
        totals=EstimationTotals(
            total_wall_area_sqm=round(total_area, 2),
            total_wall_volume_cum=round(total_volume, 2)
        ),
        message="Wall quantity estimation completed successfully"
    )
