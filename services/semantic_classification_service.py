from typing import List, Dict, Any
from schemas.semantic_classification import ClassifiedWall, SemanticClassificationResponse

def classify_walls_semantically(walls: List[Dict[str, Any]]) -> SemanticClassificationResponse:
    """
    Classifies walls into EXTERNAL, INTERNAL, LOAD_BEARING, or NON_LOAD_BEARING.
    Uses geometry heuristics like thickness and layout context.
    """
    if not walls:
        return SemanticClassificationResponse(
            classified_walls=[],
            overall_classification_quality="LOW"
        )

    classified_walls = []
    
    # Heuristics:
    # External Walls: Thicker (usually >= 230mm)
    # Internal Walls: Thinner (<= 150mm usually partitions)
    # Load-Bearing: Thicker internal walls or specific structural members
    
    # For perimeter detection, we'd need coordinates, but since we only have labels/lengths
    # from the geometry service, we rely heavily on thickness and relative count.
    
    avg_thickness = sum(w['thickness_mm'] for w in walls) / len(walls)
    
    for wall in walls:
        w_id = wall['wall_id']
        thickness = wall['thickness_mm']
        geom_conf = wall['confidence']
        
        wall_type = "INTERNAL" # Default
        reasoning = "Standard partition thickness"
        conf = geom_conf * 0.9 # Classification is an inference
        
        # 1. External Wall Heuristic
        if thickness >= 230:
            wall_type = "EXTERNAL"
            reasoning = f"Greater thickness ({thickness}mm) suggests external/envelope wall"
        
        # 2. Internal Partition Heuristic
        elif thickness <= 150:
            wall_type = "NON_LOAD_BEARING"
            reasoning = f"Thin partition ({thickness}mm) typically non-structural"
            
        # 3. Load-Bearing Internal
        elif 150 < thickness < 230:
            # If it's thicker than a partition but thinner than external
            wall_type = "INTERNAL"
            # It might be load-bearing if it's thicker than avg partitions
            if thickness > 200:
                wall_type = "LOAD_BEARING"
                reasoning = "Thicker internal wall suggests structural load-bearing role"
            else:
                reasoning = "Standard internal separation wall"

        classified_walls.append(ClassifiedWall(
            wall_id=w_id,
            length_m=wall['length_m'],
            thickness_mm=thickness,
            wall_type=wall_type,
            classification_confidence=round(conf, 2),
            reasoning=reasoning
        ))

    # Quality check
    quality = "HIGH" if len(classified_walls) > 0 else "LOW"
    
    return SemanticClassificationResponse(
        classified_walls=classified_walls,
        overall_classification_quality=quality
    )
