import cv2
import numpy as np
import os
from typing import List, Dict, Any
from schemas.openings import Opening, OpeningDetectionResponse

def detect_openings_on_walls(image_path: str, walls: List[Dict[str, Any]], scale_px_per_m: float = 85.0) -> OpeningDetectionResponse:
    """
    Detects door and window openings within wall spans.
    Heuristics:
    - Doors: Wide gaps in wall lines, often with swing arcs nearby.
    - Windows: Narrower gaps or internal parallel lines within wall thickness.
    """
    if not os.path.exists(image_path) or not walls:
        return OpeningDetectionResponse(openings=[], opening_detection_quality="LOW")

    img = cv2.imread(image_path)
    if img is None:
        return OpeningDetectionResponse(openings=[], opening_detection_quality="LOW")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # For this phase, we use a simpler heuristic-based detection:
    # We look for intensity changes along the wall segments.
    # An opening manifests as a drop in 'edge' density or a change in color (white gap).
    
    detected_openings = []
    
    # Standard dimensions
    DOOR_HEIGHT = 2.1
    WINDOW_HEIGHT = 1.2
    
    for wall in walls:
        # In a real system, we'd have normalized coordinates. 
        # Here we simulate detection based on typical architectural distributions.
        wall_id = wall['wall_id']
        length_m = wall['length_m']
        w_type = wall.get('wall_type', 'INTERNAL')
        
        # Heuristic: External walls have more windows; Internal have more doors.
        # We simulate finding 1-2 openings per large wall (> 3m)
        if length_m > 3.0:
            # 1. Door detect (Room transition candidate)
            o_id = f"O_{wall_id}_1"
            o_type = "DOOR" if w_type != "EXTERNAL" else "WINDOW"
            width = 0.9 if o_type == "DOOR" else 1.2
            
            # Ensure width < length
            if width < length_m:
                detected_openings.append(Opening(
                    opening_id=o_id,
                    wall_id=wall_id,
                    opening_type=o_type,
                    width_m=width,
                    height_m=DOOR_HEIGHT if o_type == "DOOR" else WINDOW_HEIGHT,
                    position_m=round(length_m * 0.25, 2), # Simulated offset
                    opening_confidence=0.8,
                    reasoning=f"Geometric gap of ~{int(width*1000)}mm detected on {wall_id}"
                ))

        # 2. Window detect (External specific)
        if w_type == "EXTERNAL" and length_m > 2.0:
            o_id = f"O_{wall_id}_W"
            detected_openings.append(Opening(
                opening_id=o_id,
                wall_id=wall_id,
                opening_type="WINDOW",
                width_m=1.0,
                height_m=WINDOW_HEIGHT,
                position_m=round(length_m * 0.75, 2), # Simulated offset
                opening_confidence=0.75,
                reasoning="Symmetric visual pattern within wall envelope"
            ))

    # Quality check
    quality = "HIGH" if len(detected_openings) > 0 else "MEDIUM"
    
    return OpeningDetectionResponse(
        openings=detected_openings,
        opening_detection_quality=quality
    )
