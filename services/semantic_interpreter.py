import re
from typing import Dict, List, Tuple, Optional

from services.ai_interpreter import interpret_text_rule_based, normalize_measurement

def normalize_to_meters(measurement: str) -> Optional[float]:
    normalized, _ = normalize_measurement(measurement)
    return normalized

def is_wall_related(label: str) -> bool:
    wall_keywords = ['WALL', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9',
                     'EXTERNAL', 'INTERNAL', 'EXT', 'INT', 'PARTITION']
    label_upper = label.upper()
    for keyword in wall_keywords:
        if keyword in label_upper:
            return True
    return False

def is_non_wall_element(label: str) -> bool:
    non_wall_keywords = ['DOOR', 'WINDOW', 'FURNITURE', 'FIXTURE', 'COLUMN']
    label_upper = label.upper()
    for keyword in non_wall_keywords:
        if keyword in label_upper:
            return True
    return False

def extract_wall_identifier(text: str) -> Optional[str]:
    w_num = re.search(r'\bW\s*(\d+)\b', text, re.IGNORECASE)
    if w_num:
        return f"W{w_num.group(1)}"
    
    wall_letter = re.search(r'\bWall\s+([A-Z])\b', text, re.IGNORECASE)
    if wall_letter:
        return f"Wall {wall_letter.group(1).upper()}"
    
    if re.search(r'\bExternal\s+Wall\b', text, re.IGNORECASE):
        return "External Wall"
    if re.search(r'\bInternal\s+Wall\b', text, re.IGNORECASE):
        return "Internal Wall"
    if re.search(r'\bEXT\b', text, re.IGNORECASE):
        return "EXT"
    if re.search(r'\bINT\b', text, re.IGNORECASE):
        return "INT"
    
    return None

def interpret_walls(clean_text: str, measurements: List[str], labels: List[str]) -> Dict:
    """Interpret walls from cleaned OCR text using the stronger AI interpreter."""
    try:
        interpreted_data, confidence = interpret_text_rule_based(clean_text)
    except Exception:
        return {
            'walls': [],
            'assumed_wall_height_m': 3.0,
            'confidence': 'low'
        }

    walls = [
        {'label': wall.label, 'length_m': wall.length_m}
        for wall in interpreted_data.walls
    ]

    return {
        'walls': walls,
        'assumed_wall_height_m': interpreted_data.assumed_wall_height_m,
        'confidence': confidence
    }
