import re
from typing import Any, Dict, List, Optional

KEYWORDS = {
    'rooms': [r'\broom\b', r'\brooms\b', r'\bsitting room\b', r'\bsitting\b', r'\bshade\b'],
    'bedrooms': [r'\bbedroom\b', r'\bbedrooms\b', r'\bbdr\b', r'\bbedrm\b', r'\bbr\b', r'\bmaster\b'],
    'bathrooms': [r'\bbathroom\b', r'\bbathrooms\b', r'\bwc\b', r'\bw\.c\.\b', r'\btoilet\b', r'\bshower\b', r'\bsh\b'],
    'kitchens': [r'\bkitchen\b', r'\bkitchens\b', r'\bkit\b'],
    'living_rooms': [r'\bliving room\b', r'\bloungeroom\b', r'\bfamily room\b', r'\blounge\b', r'\bliving\b'],
    'dining_rooms': [r'\bdining room\b', r'\bdining\b'],
    'stores': [r'\bstore\b', r'\bstorage\b', r'\bstores\b', r'\bstorey\b'],
    'doors': [r'\bdoor\b', r'\bdoors\b'],
    'windows': [r'\bwindow\b', r'\bwindows\b', r'\bfenestration\b'],
    'columns': [r'\bcolumn\b', r'\bcolumns\b', r'\bcol\b'],
    'beams': [r'\bbeam\b', r'\bbeams\b', r'\bblm\b', r'\bblk\b'],
}

# Patterns for extracting UNIQUE numbered room instances from plan text
# "Bedroom 1", "Bedroom 2", "Master Bedroom" -> 3 unique bedrooms, not 15 keyword hits
_UNIQUE_ROOM_PATTERNS = {
    'bedrooms': [
        r'\bmaster\s+bed(?:room)?\b',
        r'\bbed(?:room)?\s*(\d+)\b',
        r'\bbdr\s*(\d+)\b',
        r'\bbedrm\s*(\d+)\b',
    ],
    'bathrooms': [
        r'\bbath(?:room)?\s*(\d+)\b',
        r'\bw\.?c\.?\s*(\d+)\b',
        r'\btoilet\s*(\d+)\b',
        r'\ben[-\s]suite\b',
    ],
    'kitchens': [
        r'\bkitchen\s*(\d+)\b',
        r'\bkit\s*(\d+)\b',
    ],
    'living_rooms': [
        r'\bliving\s+room\s*(\d+)\b',
        r'\blounge\s*(\d+)\b',
        r'\bfamily\s+room\s*(\d+)\b',
    ],
    'dining_rooms': [
        r'\bdining\s+room\s*(\d+)\b',
    ],
    'stores': [
        r'\bstore\s*room\s*(\d+)\b',
        r'\bstorage\s*(\d+)\b',
    ],
}


def _count_unique_instances(text: str, category: str) -> int:
    """
    Count unique room/element instances.

    - Numbered rooms: 'Bedroom 1', 'Bedroom 2' -> 2
    - Named rooms: 'Master Bedroom', 'En-suite' -> 1 each
    This prevents schedule tables from inflating the count.
    For unlabelled plans (no hits found), returns 0 so QS fallback kicks in.
    """
    if not text or category not in _UNIQUE_ROOM_PATTERNS:
        return 0

    unique_instances = set()
    lower_text = text.lower()

    for pat in _UNIQUE_ROOM_PATTERNS[category]:
        for m in re.finditer(pat, lower_text, re.IGNORECASE):
            if m.lastindex and m.group(1):
                # Numbered: "Bedroom 1" -> key "bedrooms_1"
                unique_instances.add(f"{category}_{m.group(1)}")
            else:
                # Named but unnumbered: "master bedroom"
                unique_instances.add(m.group(0).strip())

    return len(unique_instances)


def _count_matches(text: str, patterns: List[str]) -> int:
    """Count keyword occurrences (for structural elements only)."""
    if not text:
        return 0
    count = 0
    for pat in patterns:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        if matches:
            count += len(matches)
    return count


def analyze_building_components(
    raw_text: str,
    labels: List[str],
    walls: List[Dict[str, Any]],
    yolo_counts: Dict[str, int] = None,
    plan_text: Optional[str] = None
) -> Dict[str, int]:
    """
    Analyze building components from OCR text and YOLO detections.

    Args:
        raw_text:    Full cleaned OCR text.
        labels:      Extracted label tokens.
        walls:       Detected wall segments.
        yolo_counts: YOLO detection counts (override OCR for physical elements).
        plan_text:   Schedule-stripped text for accurate room counting.
                     Falls back to raw_text if not provided (handles unlabelled plans).
    """
    # Room counting uses schedule-stripped text when available
    room_text  = (plan_text or raw_text or "").lower()
    full_text  = (raw_text or "").lower()
    label_text = " ".join(labels).lower() if labels else ""

    # --- Unique instance counting for rooms (schedule-safe) ---
    bedrooms     = _count_unique_instances(room_text, 'bedrooms')
    bathrooms    = _count_unique_instances(room_text, 'bathrooms')
    kitchens     = _count_unique_instances(room_text, 'kitchens')
    living_rooms = _count_unique_instances(room_text, 'living_rooms')
    dining_rooms = _count_unique_instances(room_text, 'dining_rooms')
    stores       = _count_unique_instances(room_text, 'stores')

    # For unlabelled plans: unique counting returns 0 -> fall back to keyword presence (capped at 1)
    if bedrooms == 0:
        bedrooms = min(1, _count_matches(room_text, KEYWORDS['bedrooms']))
    if kitchens == 0:
        kitchens = min(1, _count_matches(room_text, KEYWORDS['kitchens']))
    if bathrooms == 0:
        bathrooms = min(1, _count_matches(room_text, KEYWORDS['bathrooms']))

    # Generic "room" keyword count, capped to avoid schedule inflation
    room_kw = _count_matches(room_text, KEYWORDS['rooms'])
    rooms = min(room_kw, 10)

    # --- Structural elements: full text + labels, normal counting ---
    joined_full = f"{full_text} {label_text}"
    doors   = _count_matches(joined_full, KEYWORDS['doors'])
    windows = _count_matches(joined_full, KEYWORDS['windows'])
    columns = _count_matches(joined_full, KEYWORDS['columns'])
    beams   = _count_matches(joined_full, KEYWORDS['beams'])

    counts = {
        'rooms':         rooms,
        'bedrooms':      bedrooms,
        'bathrooms':     bathrooms,
        'kitchens':      kitchens,
        'living_rooms':  living_rooms,
        'dining_rooms':  dining_rooms,
        'stores':        stores,
        'walls':         len(walls or []),
        'doors':         doors,
        'windows':       windows,
        'columns':       columns,
        'beams':         beams,
        'stairs':        0,
        'other_elements': 0,
    }

    # YOLO overrides for physically detected elements
    if yolo_counts:
        for comp in ['doors', 'windows', 'columns', 'stairs']:
            if comp in yolo_counts and yolo_counts[comp] > 0:
                counts[comp] = yolo_counts[comp]

    detected_tokens = len(labels or [])
    known_total = sum(counts[k] for k in KEYWORDS.keys())
    counts['other_elements'] = max(0, detected_tokens - known_total)

    return counts
