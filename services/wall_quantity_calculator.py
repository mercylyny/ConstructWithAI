from typing import List, Dict, Any

def calculate_wall_quantities(walls: List[Dict[str, Any]], wall_height: float) -> Dict[str, Any]:
    """
    Calculates Area (sqm) and Volume (cum) for interpreted walls.
    
    Args:
        walls: List of dicts, each containing 'label' and 'length_m'.
        wall_height: Global wall height in meters.
        
    Returns:
        Dict containing detailed wall data and totals.
    """
    estimated_walls = []
    total_area = 0.0
    total_volume = 0.0
    
    # Defaults
    thickness_load_bearing = 0.20
    thickness_partition = 0.15
    default_thickness = 0.20
    
    for wall in walls:
        label = wall.get('label', '')
        length_m = wall.get('length_m', 0.0)
        
        # Determine thickness
        # Simple heuristic: "Partition" or "INT" -> 0.15, otherwise 0.20
        # This can be expanded later
        if "PARTITION" in label.upper() or "INT" in label.upper():
            thickness = thickness_partition
        else:
            # Default to load bearing / external / standard
            thickness = default_thickness
            
        area_sqm = round(length_m * wall_height, 2)
        volume_cum = round(area_sqm * thickness, 2)
        
        estimated_walls.append({
            "label": label,
            "length_m": length_m,
            "height_m": wall_height,
            "thickness_m": thickness,
            "area_sqm": area_sqm,
            "volume_cum": volume_cum
        })
        
        total_area += area_sqm
        total_volume += volume_cum
        
    return {
        "walls": estimated_walls,
        "totals": {
            "total_wall_area_sqm": round(total_area, 2),
            "total_wall_volume_cum": round(total_volume, 2)
        }
    }
