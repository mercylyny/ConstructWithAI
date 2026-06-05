from typing import List, Dict, Any
from schemas.masonry import ClassifiedMasonrySegment, MasonryClassificationResponse

def classify_masonry_details(segments: List[Dict[str, Any]]) -> MasonryClassificationResponse:
    """
    Classifies wall segments based on thickness and determines the overall project masonry system.
    """
    if not segments:
        return MasonryClassificationResponse(classified_segments=[], project_masonry_system="BLOCK")

    classified_list = []
    has_brick = False
    has_block = False
    
    for seg in segments:
        thickness = seg['normalized_thickness_mm']
        conf = seg.get('segment_confidence', 0.8)
        
        # 1. Type Mapping
        if thickness == 230:
            m_type = "BRICK"
            has_brick = True
        else:
            m_type = "BLOCK"
            has_block = True
            
        # 2. Role Mapping
        if 100 <= thickness <= 150:
            m_role = "PARTITION"
        elif 200 <= thickness <= 230:
            m_role = "LOAD_BEARING"
        elif thickness >= 300:
            m_role = "STRUCTURAL"
        else:
            m_role = "PARTITION" # Default fallback
            
        classified_list.append(ClassifiedMasonrySegment(
            segment_id=seg['segment_id'],
            masonry_type=m_type,
            masonry_role=m_role,
            confidence=conf
        ))
        
    # 3. Project-wide System Detection
    if has_brick and has_block:
        proj_system = "HYBRID"
    elif has_brick:
        proj_system = "BRICK"
    else:
        proj_system = "BLOCK"
        
    return MasonryClassificationResponse(
        classified_segments=classified_list,
        project_masonry_system=proj_system
    )
