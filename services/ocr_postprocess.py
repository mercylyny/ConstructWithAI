"""
Phase 7.3.2: OCR Post-processing and Structured Data Extraction
Transforms raw OCR text into clean, structured, machine-readable data.

Fix 3 (2026-06-02): Improved extraction for floor-plan drawings:
- extract_labels: now matches mixed-case room words (bedroom, kitchen, bathroom, shade…)
- extract_measurements: now captures dimension chains like "200  3.300  200  3.500"
- extract_scale: new helper that reads SCALE1100 / 1:100 annotations
- postprocess_ocr: returns 'scale_ratio' in the output dict
"""
import re
from typing import List, Dict, Optional

# ---------------------------------------------------------------------------
# Step 1: Text cleaning
# ---------------------------------------------------------------------------

def clean_ocr_text(text: str) -> str:
    """
    Clean raw OCR text by removing noise and normalising formatting.
    """
    if not text:
        return ""

    # Remove non-printable characters except newlines and tabs
    cleaned = ''.join(char for char in text if char.isprintable() or char in '\n\t')

    # Normalise line breaks
    cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')

    # Collapse runs of 3+ blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # Collapse multiple spaces
    cleaned = re.sub(r' {2,}', ' ', cleaned)

    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in cleaned.split('\n')]
    cleaned = '\n'.join(lines)

    # Remove obvious OCR box-drawing garbage
    garbage_patterns = [
        r'[░▒▓█■□▪▫]',
        r'[┌┐└┘├┤┬┴┼─│]',
        r'[©®™]',
        r'[•·∙](?!\d)',
    ]
    for pattern in garbage_patterns:
        cleaned = re.sub(pattern, '', cleaned)

    # Drop lines that are only special characters
    lines = [line for line in cleaned.split('\n')
             if line and not re.match(r'^[^\w\s]+$', line)]

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Step 1b: Strip schedule/table sections (NEW)
# ---------------------------------------------------------------------------

def strip_schedule_sections(text: str) -> str:
    """
    Remove schedule/table sections from OCR text before room counting.

    Architectural plans often include 'DOOR SCHEDULE' and 'WINDOW SCHEDULE'
    tables that repeat room names (e.g. 'Bedroom 1') once for every door or
    window associated with that room. Without filtering, this inflates the
    AI's room/bedroom counts massively.

    This function detects schedule section headers and strips everything
    until the next major drawing section is found.
    """
    if not text:
        return text

    # Headers that signal the START of a schedule block
    schedule_headers = [
        r'door[s]?\s+sched',
        r'window[s]?\s+sched',
        r'room[s]?\s+sched',
        r'finishe?s?\s+sched',
        r'ironmongery\s+sched',
        r'hardware\s+sched',
        r'fitting[s]?\s+sched',
    ]

    # Keywords that signal the END of a schedule block (next drawing section)
    end_markers = [
        r'floor\s+plan',
        r'ground\s+floor',
        r'first\s+floor',
        r'elevation',
        r'\bsection\b',
        r'site\s+plan',
        r'site\s+layout',
        r'roof\s+plan',
        r'general\s+notes',
        r'specification',
        r'scale\s*1\s*[:/]',
    ]

    lines = text.split('\n')
    result_lines = []
    in_schedule = False
    schedule_line_count = 0
    MAX_SCHEDULE_LINES = 80  # Safety cap: never skip more than 80 lines

    for line in lines:
        line_lower = line.lower().strip()

        # Detect start of a schedule section
        if not in_schedule and any(re.search(p, line_lower) for p in schedule_headers):
            in_schedule = True
            schedule_line_count = 0
            # Keep the header so we know what was stripped
            result_lines.append(f'[SCHEDULE STRIPPED: {line.strip()}]')
            continue

        if in_schedule:
            schedule_line_count += 1
            # End the schedule if we hit a new section OR exceed the safety cap
            if schedule_line_count > MAX_SCHEDULE_LINES or any(
                re.search(p, line_lower) for p in end_markers
            ):
                in_schedule = False
                result_lines.append(line)  # Keep the end-marker line
            # Otherwise skip schedule rows
            continue

        result_lines.append(line)

    return '\n'.join(result_lines)


# ---------------------------------------------------------------------------
# Step 2: Scale extraction (new)
# ---------------------------------------------------------------------------

def extract_scale(text: str) -> Optional[float]:
    """
    Detect the drawing scale and return the denominator as a float.

    Handles:
      - SCALE1100, SCALE1:100, SCALE 1:100
      - 1:100, 1:50, 1:200  (standalone)
      - SCALE1-100

    Returns the denominator (e.g. 100.0 for 1:100) or None if not found.
    The denominator is used to scale measurements: real_m = drawn_m * denominator.
    For example, a 3.3 cm line on a 1:100 plan = 3.3 m in reality.
    NOTE: Since the measurements extracted by extract_measurements() already
    convert to metres, the scale ratio is informational here — the real use
    is confirming that on-plan values ARE in metres (i.e. scale ≤ 1:100).
    """
    if not text:
        return None

    # Merge run-on: SCALE1100 → SCALE 1:100
    merged = re.sub(r'(?i)SCALE\s*1[\s\-:]*(\d+)', lambda m: f'SCALE1:{m.group(1)}', text)

    match = re.search(r'(?i)(?:scale\s*)?1\s*[:/\-]\s*(\d+)', merged)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------------------
# Step 3: Measurement extraction (enhanced)
# ---------------------------------------------------------------------------

def extract_measurements(text: str) -> List[str]:
    """
    Extract all dimensional values from OCR text.

    Handles:
    - Explicit unit: 1200mm, 3.5m, 240cm
    - Dimension pairs: 3.5x2.8, 240x1200mm
    - Spaced thousands: 1 200mm, 3 600
    - Bare decimal metres on a floor plan: 3.300, 2.300, 1.500  (0.5 – 20.0)
    - Bare millimetre integers: 900, 1200, 3300  (>= 300 and < 20001)
    - Dimension chains: '200  3.300  200  3.500  200'  (each number extracted)
    """
    if not text:
        return []

    measurements = []

    # Pattern 1: Explicit units (3.5m, 1200mm, 240cm)
    p1 = r'\b(\d+(?:\.\d+)?)\s*(?:mm|cm|m|meters?)\b'
    for m in re.finditer(p1, text, re.IGNORECASE):
        measurements.append(m.group(0).strip())

    # Pattern 2: Dimension pairs (3.5x2.8, 10x20, 240x1200mm)
    p2 = r'\b(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)\s*(?:mm|cm|m|meters?)?\b'
    for m in re.finditer(p2, text, re.IGNORECASE):
        measurements.append(m.group(0).strip())

    # Pattern 3: Spaced thousands (1 200mm, 3 600)
    p3 = r'\b(\d+)\s+(\d{3})\s*(?:mm|cm|m)?\b'
    for m in re.finditer(p3, text, re.IGNORECASE):
        measurements.append(m.group(0).strip())

    # Pattern 4: Bare decimal values in the range 0.5–20.0 (likely metres on plan)
    p4 = r'\b(\d{1,2}\.\d{1,3})\b'
    for m in re.finditer(p4, text):
        try:
            val = float(m.group(1))
            if 0.5 <= val <= 20.0:
                measurements.append(m.group(0).strip())
        except ValueError:
            pass

    # Pattern 5: Bare integers that are plausible millimetres (300–20000)
    # e.g. 900, 1200, 3300, 3500 on a plan with no units written
    p5 = r'\b(\d{3,5})\b'
    for m in re.finditer(p5, text):
        try:
            val = int(m.group(1))
            if 300 <= val <= 20000:
                # Only add if not already captured by pattern 1–4
                candidate = m.group(0).strip()
                if candidate not in measurements:
                    measurements.append(candidate)
        except ValueError:
            pass

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for item in measurements:
        key = item.lower().replace(' ', '')
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


# ---------------------------------------------------------------------------
# Step 4: Label extraction (enhanced)
# ---------------------------------------------------------------------------

# Explicit room/element keywords to always capture regardless of case
_PLAN_KEYWORDS = [
    # Rooms
    'bedroom', 'bed room', 'master bedroom', 'master bed',
    'bathroom', 'bath room', 'wc', 'toilet', 'shower',
    'kitchen', 'kit',
    'living room', 'living', 'lounge', 'sitting room', 'sitting',
    'dining room', 'dining',
    'store', 'storage', 'storeroom',
    'shade', 'veranda', 'verandah', 'porch',
    'garage', 'carport',
    'office', 'study',
    'corridor', 'hallway', 'hall', 'passage',
    # Structure
    'door', 'window', 'column', 'col', 'beam', 'blm',
    'footing', 'foundation', 'slab',
    # Drawing metadata
    'ground floor', 'first floor', 'roof plan', 'section',
]

def extract_labels(text: str) -> List[str]:
    """
    Extract plan element labels from OCR text.

    Strategy:
    1. Check for known architectural keywords (case-insensitive).
       Also checks whether a keyword is *embedded* inside a larger token
       (e.g. 'kitchen' inside 'SWKITCHEN').
    2. Fall back to uppercase-token scan for grid refs and abbreviations.
    """
    if not text:
        return []

    labels = []
    lower_text = text.lower()
    # All whitespace-separated tokens in lowercase for substring scan
    all_tokens = re.findall(r'[A-Za-z]{2,}', lower_text)

    # Step A: keyword scan — whole-word match OR substring inside any token
    for keyword in _PLAN_KEYWORDS:
        whole_word_pattern = r'\b' + re.escape(keyword) + r'\b'
        found = bool(re.search(whole_word_pattern, lower_text))
        if not found:
            # Fallback: embedded match inside any token (e.g. 'kitchen' in 'swkitchen')
            found = any(keyword in token for token in all_tokens)
        if found:
            labels.append(keyword)

    # Step B: uppercase token scan for abbreviations not in the keyword list
    noise_words = {
        'PAGE', 'LOW', 'CONFIDENCE', 'OCR', 'FAILED',
        'THE', 'AND', 'OR', 'FOR', 'TO', 'OF', 'IN', 'ON', 'AT', 'BY', 'AS',
        'PDF', 'PNG', 'JPG', 'JPEG', 'SCALE', 'NO', 'REF', 'MM', 'CM',
    }
    uc_pattern = r'\b([A-Z]{2,}(?:[/\-][A-Z]{2,})?(?:\s+[A-Z]{2,})?)\b'
    for m in re.finditer(uc_pattern, text):
        label = m.group(1).strip()
        if label in noise_words:
            continue
        if len(set(label.replace(' ', ''))) == 1:
            continue  # All same char — OCR line noise
        labels.append(label.lower())

    # Deduplicate
    seen = set()
    unique = []
    for label in labels:
        if label not in seen:
            seen.add(label)
            unique.append(label)

    return unique


# ---------------------------------------------------------------------------
# Step 5: Full pipeline
# ---------------------------------------------------------------------------

def postprocess_ocr(raw_text: str) -> Dict[str, object]:
    """
    Complete OCR post-processing pipeline.

    Returns:
        dict with keys:
          - clean_text   : cleaned OCR text (includes all text, used for wall parsing)
          - plan_text    : cleaned text with schedule sections stripped (used for room counting)
          - measurements : list of detected measurement strings
          - labels       : list of detected plan element labels
          - scale_ratio  : drawing scale denominator (e.g. 100 for 1:100) or None
    """
    clean_text = clean_ocr_text(raw_text)

    # Strip schedule tables for room counting (prevents inflation from schedules)
    plan_text = strip_schedule_sections(clean_text)

    measurements = extract_measurements(clean_text)  # Use full text for measurements
    labels = extract_labels(plan_text)               # Use stripped text for labels
    scale_ratio = extract_scale(clean_text)

    return {
        "clean_text": clean_text,
        "plan_text": plan_text,
        "measurements": measurements,
        "labels": labels,
        "scale_ratio": scale_ratio,
    }
