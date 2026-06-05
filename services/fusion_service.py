from typing import List, Dict, Optional
from schemas.estimation import WallQuantity

def fuse_estimation_data(ocr_walls: List[WallQuantity], manual_walls: Optional[List[WallQuantity]]) -> List[WallQuantity]:
    """
    Fuses OCR-derived wall data with manual user inputs based on a strict authority hierarchy.
    
    Hierarchy:
    1. MANUAL (Highest Authority)
    2. OCR (Medium Authority)
    3. INFERRED (Lowest Authority)
    
    Fusion Rules:
    - If manual walls exist, they MUST be included.
    - If a manual wall matches an OCR wall (by label), manual values override.
    - OCR walls that don't match manual inputs are kept (unless explicitly deleted - logic for future).
    - Confidence scores are recalculated based on the source.
    """
    if not manual_walls:
        # No manual input? Return OCR walls but tag them if not already tagged
        for w in ocr_walls:
            # If weight is 0 (default), assign OCR default
            if w.confidence_weight == 0.0:
                 w.data_source = "OCR"
                 w.confidence_weight = 0.7 # Default OCR confidence
        return ocr_walls

    fused_walls = []
    
    # Index manual walls by label for quick lookup
    manual_map = {w.label.upper(): w for w in manual_walls}
    
    # Track which manual walls have been used
    used_manual_labels = set()
    
    # 1. Process OCR walls
    for ocr_wall in ocr_walls:
        label_key = ocr_wall.label.upper()
        
        if label_key in manual_map:
            # MATCH FOUND: Fusion needed
            manual_wall = manual_map[label_key]
            
            # Create a hybrid wall
            # Start with OCR data
            hybrid_wall = ocr_wall.model_copy()
            
            # Override with Manual data (assuming manual input is truth)
            # In a real UI, we might have partial manual updates (e.g. just length). 
            # For now, we assume if a manual wall is provided, its fields are authoritative.
            hybrid_wall.length_m = manual_wall.length_m
            hybrid_wall.height_m = manual_wall.height_m
            hybrid_wall.thickness_m = manual_wall.thickness_m
            
            # Recalculate physicals just in case
            hybrid_wall.area_sqm = round(hybrid_wall.length_m * hybrid_wall.height_m, 2)
            hybrid_wall.volume_cum = round(hybrid_wall.area_sqm * hybrid_wall.thickness_m, 2)
            
            hybrid_wall.data_source = "HYBRID"
            hybrid_wall.confidence_weight = 0.95 # High confidence due to manual verification
            
            fused_walls.append(hybrid_wall)
            used_manual_labels.add(label_key)
        else:
            # NO MATCH: Keep OCR wall
            ocr_wall.data_source = "OCR"
            ocr_wall.confidence_weight = 0.7
            fused_walls.append(ocr_wall)
            
    # 2. Add remaining Manual walls (newly added by user)
    for manual_wall in manual_walls:
        if manual_wall.label.upper() not in used_manual_labels:
            manual_wall.data_source = "MANUAL"
            manual_wall.confidence_weight = 1.0 # Highest confidence
            
            # Ensure physicals are calculated
            if manual_wall.area_sqm == 0:
                 manual_wall.area_sqm = round(manual_wall.length_m * manual_wall.height_m, 2)
            if manual_wall.volume_cum == 0:
                 manual_wall.volume_cum = round(manual_wall.area_sqm * manual_wall.thickness_m, 2)
            
            fused_walls.append(manual_wall)
            
    return fused_walls
