from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ConfidenceReport(BaseModel):
    confidence_score: float
    confidence_level: str
    warnings: List[str]
    assumptions: List[str]
    message: str

def analyze_estimation_confidence(data: Dict[str, Any]) -> ConfidenceReport:
    """
    Analyzes the available project data to calculate a confidence score
    and identifying potential issues/assumptions.
    
    Data dictionary expectations (optional keys):
    - 'ocr_text': str
    - 'walls': List[dict] (from interpreted/estimated output)
    - 'quantities': dict
    - 'custom_rates': dict/base object
    - 'scale_provided': bool
    """
    score = 1.0
    warnings = []
    assumptions = []
    
    # Extract Data
    ocr_text = data.get("ocr_text", "")
    walls = data.get("walls", [])
    custom_rates = data.get("custom_rates")
    scale_provided = data.get("scale_provided", False)
    
    # --- Rule 1: OCR Text Quality (Weight: 0.2) ---
    if not ocr_text:
        # If no text provided, we can't judge quality, but if it was expected:
        warnings.append("No OCR text provided for analysis.")
    elif len(ocr_text) < 50:
        score -= 0.15
        warnings.append("OCR text is very short/sparse. Plan might be unclear.")
    
    # --- Rule 2: Wall Detection (Weight: 0.3) ---
    wall_count = len(walls)
    if wall_count == 0:
        score -= 0.3
        warnings.append("No walls detected in the estimation.")
    elif wall_count < 2:
        score -= 0.1
        warnings.append("Very low wall count detected (less than 2).")
    elif wall_count > 4:
        # Bonus confidence if we found a good number of walls
        score = min(1.0, score + 0.05)
        
    # --- Rule 3: Wall Height Assumptions (Weight: 0.1) ---
    # Check if any wall uses default height (assuming strict default of 3.0m if not found)
    # We'll check if walls have 'height_m' explicitly from source or if we can detect 'Assumed' flag
    # For now, simplistic check:
    using_assumed_height = any(w.get('assumed_height', False) for w in walls)
    if using_assumed_height:
        score -= 0.1
        assumptions.append("Used assumed default wall height for some walls.")

    # --- Rule 4: Scale (Weight: 0.2) ---
    if scale_provided:
        score = min(1.0, score + 0.05)
    else:
        # Implicitly, if we rely on standard pixels without scale, it's risky
        pass 
        # Note: Current pipeline doesn't strictly pass scale everywhere, so be lenient.

    # --- Rule 5: Pricing Context (Weight: 0.1) ---
    if not custom_rates:
        # Using Defaults
        assumptions.append("Using default market rates (Uganda Context). Prices may vary.")
    else:
        # Custom rates provided
        score = min(1.0, score + 0.05)
        
    # Sanitize Score
    score = max(0.0, min(1.0, score))
    
    # Determine Level
    if score >= 0.8:
        level = "High"
    elif score >= 0.5:
        level = "Medium"
    else:
        level = "Low"
        
    return ConfidenceReport(
        confidence_score=round(score, 2),
        confidence_level=level,
        warnings=warnings,
        assumptions=assumptions,
        message="Confidence analysis complete."
    )
