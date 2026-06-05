from typing import List, Dict, Any
from schemas.normalization import WallSegment, NormalizationResponse
import math

def normalize_and_segment_walls(walls: List[Dict[str, Any]]) -> NormalizationResponse:
    """
    Normalizes wall thickness to standard sizes and segments long walls (>6m).
    Assumes each wall has wall_id, length_m, height_m, thickness_mm, and net_area.
    """
    if not walls:
        return NormalizationResponse(wall_segments=[], segmentation_quality="LOW")

    standard_thicknesses = [100, 150, 200, 230, 300]
    MAX_LENGTH = 6.0
    
    wall_segments = []
    
    for wall in walls:
        w_id = wall['wall_id']
        length = wall['length_m']
        height = wall.get('height_m', 3.0) # Default height if missing
        net_area = wall.get('net_area_m2', length * height)
        orig_thickness = wall['thickness_mm']
        geom_conf = wall.get('confidence', 0.8)
        
        # 1. Normalize Thickness
        norm_thickness = min(standard_thicknesses, key=lambda x: abs(x - orig_thickness))
        deviation = abs(norm_thickness - orig_thickness)
        review_flag = deviation > 20
        
        # Apply normalization penalty to confidence
        thickness_conf_factor = 0.95 if norm_thickness != orig_thickness else 1.0
        
        # 2. Segmentation
        num_segments = math.ceil(length / MAX_LENGTH)
        segment_length = length / num_segments
        segment_area = net_area / num_segments
        
        segmentations_penalty = 0.98 if num_segments > 1 else 1.0
        
        final_conf = round(geom_conf * thickness_conf_factor * segmentations_penalty, 2)
        
        for i in range(num_segments):
            seg_id = f"{w_id}-S{i+1}" if num_segments > 1 else w_id
            
            wall_segments.append(WallSegment(
                segment_id=seg_id,
                parent_wall_id=w_id,
                segment_length_m=round(segment_length, 2),
                segment_height_m=round(height, 2),
                segment_net_area_m2=round(segment_area, 2),
                normalized_thickness_mm=norm_thickness,
                original_thickness_mm=orig_thickness,
                segment_confidence=final_conf,
                review_flag=review_flag
            ))

    quality = "HIGH" if len(wall_segments) > 0 else "LOW"
    
    return NormalizationResponse(
        wall_segments=wall_segments,
        segmentation_quality=quality
    )
