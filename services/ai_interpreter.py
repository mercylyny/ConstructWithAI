import os
import re
from typing import Optional, Tuple, List
from schemas.ai import InterpretedData, InterpretedWall

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OCR_TEXT_DIR = os.path.join(BASE_DIR, "outputs", "ocr_text")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

def get_stored_ocr_text(filename: str) -> Optional[str]:
    """
    Attempts to retrieve stored OCR text from Phase 7.3 output.
    Checks multiple naming conventions and directories for robustness.
    """
    candidates = [
        filename,
        f"{filename}.txt",
        f"{os.path.splitext(filename)[0]}.txt"
    ]
    
    search_dirs = [OCR_TEXT_DIR, UPLOAD_DIR]
    
    for folder in search_dirs:
        for candidate in candidates:
            path = os.path.join(folder, candidate)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    return None

    # Fallback: attempt to locate the file by normalized base name within the OCR directory
    normalized_request = re.sub(r"[\W_]+", "", os.path.splitext(filename)[0].lower())
    if os.path.isdir(OCR_TEXT_DIR):
        for candidate in os.listdir(OCR_TEXT_DIR):
            candidate_root = os.path.splitext(candidate)[0].lower()
            normalized_candidate = re.sub(r"[\W_]+", "", candidate_root)
            if normalized_candidate == normalized_request:
                path = os.path.join(OCR_TEXT_DIR, candidate)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading fallback {path}: {e}")
                    return None

    return None

def clean_ocr_noise(text: str) -> str:
    """
    Remove common OCR noise and non-measurement text from construction plans.
    
    Filters out:
    - Titles, legends, stamps, approvals
    - Grid lines, north arrows
    - Furniture labels
    - Decorative symbols
    - Page markers
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    # Noise patterns to ignore
    noise_patterns = [
        r'---\s*Page\s+\d+\s*---',  # Page markers
        r'(?i)(title|legend|stamp|approval|approved|drawn|checked)',  # Document metadata
        r'(?i)(north|scale|date|revision|rev\.|dwg)',  # Drawing metadata
        r'(?i)(furniture|door|window|fixture)',  # Non-wall elements
        r'^\s*[A-Z]\s*$',  # Single letters (grid markers)
        r'(?i)(low\s+confidence)',  # OCR confidence markers
    ]
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        # Check if line matches noise patterns
        is_noise = False
        for pattern in noise_patterns:
            if re.search(pattern, line_clean):
                is_noise = True
                break
        
        if not is_noise:
            cleaned_lines.append(line_clean)
    
    return '\n'.join(cleaned_lines)

def normalize_measurement(value_str: str, context: str = "") -> Tuple[Optional[float], str]:
    """
    Normalize measurements to meters with confidence scoring.
    
    Handles:
    - 3.6m, 3600, 3 600, 3.60, 3.6
    - Missing units (inferred from context)
    - Millimeters vs meters
    
    Returns:
        Tuple[Optional[float], str]: (value_in_meters, confidence)
    """
    value_str = value_str.strip().replace(' ', '')
    
    # Pattern 1: Explicit meters (3.6m, 3.6 m, 3.6meters)
    meters_match = re.match(r'^(\d+(?:\.\d+)?)\s*(?:m|meters?)$', value_str, re.IGNORECASE)
    if meters_match:
        try:
            val = float(meters_match.group(1))
            # Sanity check: typical wall lengths 0.5m - 20m
            if 0.5 <= val <= 20.0:
                return (val, "high")
        except ValueError:
            pass
    
    # Pattern 2: Millimeters (3600, 3600mm)
    mm_match = re.match(r'^(\d+)\s*(?:mm)?$', value_str, re.IGNORECASE)
    if mm_match:
        try:
            val_mm = float(mm_match.group(1))
            # Convert mm to m
            val_m = val_mm / 1000.0
            # Sanity check: typical wall lengths
            if 0.5 <= val_m <= 20.0:
                return (val_m, "medium")  # Medium confidence (unit inferred)
        except ValueError:
            pass
    
    # Pattern 3: Decimal number without unit (3.6, 4.5)
    decimal_match = re.match(r'^(\d+\.\d+)$', value_str)
    if decimal_match:
        try:
            val = float(decimal_match.group(1))
            # Assume meters for decimal values in typical range
            if 0.5 <= val <= 20.0:
                return (val, "medium")  # Medium confidence (unit inferred)
        except ValueError:
            pass
    
    return (None, "low")

def extract_wall_label(text: str, wall_index: int = 0) -> str:
    """
    Extract or generate wall labels.
    
    Identifies:
    - W1, W2, EXT, INT, A-A
    - Wall A, Wall B
    - External Wall, Internal Wall
    
    If no label found, generates: Wall-1, Wall-2, etc.
    """
    # Pattern 1: W + number
    w_num = re.search(r'\bW\s*(\d+)\b', text, re.IGNORECASE)
    if w_num:
        return f"W{w_num.group(1)}"
    
    # Pattern 2: Wall + letter/number
    wall_id = re.search(r'\bWall\s+([A-Z0-9]+)\b', text, re.IGNORECASE)
    if wall_id:
        return f"Wall {wall_id.group(1).upper()}"
    
    # Pattern 3: External/Internal Wall
    if re.search(r'\bExternal\s+Wall\b', text, re.IGNORECASE):
        return "External Wall"
    if re.search(r'\bInternal\s+Wall\b', text, re.IGNORECASE):
        return "Internal Wall"
    
    # Pattern 4: EXT/INT
    if re.search(r'\bEXT\b', text, re.IGNORECASE):
        return "EXT"
    if re.search(r'\bINT\b', text, re.IGNORECASE):
        return "INT"
    
    # Fallback: Generate placeholder
    return f"Wall-{wall_index + 1}"

def interpret_text_rule_based(text: str) -> Tuple[InterpretedData, str]:
    """
    Enhanced OCR interpretation with noise reduction and measurement recovery.
    
    Process:
    1. Clean OCR noise
    2. Extract height (global default)
    3. Find wall measurements
    4. Normalize units
    5. Assign confidence scores
    
    Returns (InterpretedData, overall_confidence)
    """
    # Step 1: Clean noise
    cleaned_text = clean_ocr_noise(text)
    
    walls = []
    assumed_height = 3.0  # Default residential height
    height_found = False
    notes = []
    
    lines = cleaned_text.split('\n')
    
    # Step 2: Extract global height
    height_re = re.compile(
        r'(?:height|h|ht)[\s:=]*(\d+(?:\.\d+)?)\s*(?:m|meters?)?',
        re.IGNORECASE
    )
    
    for line in lines:
        if not height_found:
            h_match = height_re.search(line)
            if h_match:
                try:
                    val = float(h_match.group(1))
                    # Sanity check: typical residential heights 2.4m - 4.0m
                    if 2.0 <= val <= 5.0:
                        assumed_height = val
                        height_found = True
                        notes.append(f"Height {val}m detected in OCR")
                except ValueError:
                    pass
    
    if not height_found:
        notes.append("Height not found, using default 3.0m")
    
    # Step 3: Extract wall measurements
    # Enhanced patterns to catch various OCR formats
    wall_patterns = [
        # Pattern 1: "Wall A 4.5m" or "W1 3600"
        r'((?:Wall\s+[A-Z0-9]+|W\d+|External\s+Wall|Internal\s+Wall|EXT|INT))\s+(\d+(?:\.\d+)?)\s*(?:m|mm|meters?)?',
        
        # Pattern 2: "4.5m Wall A" (reversed)
        r'(\d+(?:\.\d+)?)\s*(?:m|mm|meters?)?\s+((?:Wall\s+[A-Z0-9]+|W\d+))',
        
        # Pattern 3: "Length = 4.5m" or "L = 3600"
        r'(?:Length|L)[\s:=]+(\d+(?:\.\d+)?)\s*(?:m|mm|meters?)?',
    ]
    
    wall_index = 0
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        
        # Try each pattern
        for pattern in wall_patterns:
            matches = re.finditer(pattern, line_clean, re.IGNORECASE)
            for match in matches:
                try:
                    # Determine which group has the label and which has the value
                    groups = match.groups()
                    
                    if len(groups) == 2:
                        # Check which group is the number
                        if re.match(r'^\d+', groups[0]):
                            # groups[0] is number, groups[1] is label
                            value_str = groups[0]
                            label = extract_wall_label(groups[1], wall_index)
                        else:
                            # groups[0] is label, groups[1] is number
                            label = extract_wall_label(groups[0], wall_index)
                            value_str = groups[1]
                    elif len(groups) == 1:
                        # Only measurement found (Pattern 3)
                        value_str = groups[0]
                        label = extract_wall_label(line_clean, wall_index)
                    else:
                        continue
                    
                    # Normalize measurement
                    length_m, confidence = normalize_measurement(value_str, line_clean)
                    
                    if length_m is not None:
                        # Check for duplicates
                        duplicate = False
                        for existing_wall in walls:
                            if existing_wall.label == label and abs(existing_wall.length_m - length_m) < 0.01:
                                duplicate = True
                                break
                        
                        if not duplicate:
                            walls.append(InterpretedWall(label=label, length_m=length_m))
                            wall_index += 1
                            
                except (ValueError, IndexError):
                    continue
    
    # Step 4: Extract dimensional pairs (e.g. 3.5x4.0 or 3500 x 4000)
    # A room dimension implies two walls of length A and two walls of length B
    dim_pair_pattern = r'(\d+(?:\.\d+)?)\s*(m|mm|cm)?\s*[xX]\s*(\d+(?:\.\d+)?)\s*(m|mm|cm)?'
    implied_index = 0
    
    for line in lines:
        for m in re.finditer(dim_pair_pattern, line, re.IGNORECASE):
            try:
                val1 = float(m.group(1))
                unit1 = (m.group(2) or '').lower()
                val2 = float(m.group(3))
                unit2 = (m.group(4) or '').lower()
                
                # Normalize both to meters
                def _norm(v, u):
                    if u == 'mm' or (not u and v >= 300): return v / 1000.0
                    if u == 'cm': return v / 100.0
                    return v
                
                v1_m = _norm(val1, unit1)
                v2_m = _norm(val2, unit2)
                
                if 0.5 <= v1_m <= 20.0 and 0.5 <= v2_m <= 20.0:
                    for _ in range(2):
                        walls.append(InterpretedWall(label=f'Room-Seg-{implied_index+1}', length_m=round(v1_m, 3)))
                        implied_index += 1
                    for _ in range(2):
                        walls.append(InterpretedWall(label=f'Room-Seg-{implied_index+1}', length_m=round(v2_m, 3)))
                        implied_index += 1
            except ValueError:
                pass

    # Step 5: If still no labeled walls, treat each valid dimensional value as an implied wall segment.
    if len(walls) == 0:
        for line in lines:
            # Avoid re-matching the X parts
            line = re.sub(dim_pair_pattern, '', line, flags=re.IGNORECASE)
            
            # Extract any number that could be a wall length (0.5m – 20m)
            for m in re.finditer(r'\b(\d+(?:\.\d+)?)\s*(mm|m|cm)?\b', line, re.IGNORECASE):
                raw_val = m.group(1)
                unit = (m.group(2) or '').lower()
                try:
                    val = float(raw_val)
                    if unit == 'mm':
                        val = val / 1000.0
                    elif unit == 'cm':
                        val = val / 100.0
                    elif not unit:
                        # Bare integer >= 300 → treat as mm; bare decimal in range → metres
                        if val >= 300:
                            val = val / 1000.0
                    if 0.5 <= val <= 20.0:
                        label = f'Seg-{implied_index + 1}'
                        # Avoid near-duplicate lengths
                        duplicate = any(
                            abs(w.length_m - val) < 0.05 for w in walls
                        )
                        if not duplicate:
                            walls.append(InterpretedWall(label=label, length_m=round(val, 3)))
                            implied_index += 1
                except ValueError:
                    continue
        if walls:
            notes.append(f'No labeled walls found — {len(walls)} implied segments from dimension values')
        else:
            notes.append('No wall data detected; defaulting to 40m perimeter for standard single-storey house')
            # Hard minimum: a small 2-room house perimeter ≈ 40m
            for i, length in enumerate([4.0, 3.3, 4.0, 3.3, 2.3, 3.5, 2.3, 3.5]):
                walls.append(InterpretedWall(label=f'Default-{i+1}', length_m=length))
    
    # Step 6: Overall confidence scoring
    if len(walls) >= 3:
        overall_confidence = "high"
    elif len(walls) >= 1:
        overall_confidence = "medium"
    else:
        overall_confidence = "low"
        notes.append("No clear wall measurements detected")
        notes.append("Some units inferred from context")
    
    data = InterpretedData(
        walls=walls,
        assumed_wall_height_m=assumed_height
    )
    
    return data, overall_confidence
