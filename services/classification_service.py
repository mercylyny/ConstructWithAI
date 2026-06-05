import re
import os
from typing import Dict, Any, List
from schemas.classification import (
    PlanClassificationReport, DrawingMetadata_Custom, 
    SuitabilityScore, VisualCues, InterventionTriggers
)

def classify_drawing_suitability(filename: str, ocr_text: str, image_metadata: Dict[str, Any] = None) -> PlanClassificationReport:
    """
    Classifies a drawing based on OCR text analysis and image metadata.
    This fulfills the "Plan Analysis Intelligence" requirement.
    """
    
    # 1. Basic Metadata Extraction
    drawing_title = "Unknown Plan"
    title_match = re.search(r"(PLAN|LAYOUT|DETAIL|SECTION|ELEVATION).*", ocr_text, re.IGNORECASE)
    if title_match:
        drawing_title = title_match.group(0).strip()
    
    # Heuristic for Drawing Type
    drawing_type = "GENERAL_ARRANGEMENT"
    if any(keyword in ocr_text.lower() for keyword in ["structural", "beam", "column", "reinforcement"]):
        drawing_type = "STRUCTURAL"
    elif any(keyword in ocr_text.lower() for keyword in ["elevation", "section"]):
        drawing_type = "SECTIONAL_ELEVATION"
    elif any(keyword in ocr_text.lower() for keyword in ["layout", "floor plan"]):
        drawing_type = "ARCHITECTURAL_LAYOUT"

    # 2. Visual Cues Analysis (Simulated from OCR/Metadata)
    res_str = "Standard"
    if image_metadata and "width" in image_metadata:
        res_str = f"{image_metadata['width']}x{image_metadata['height']}"
        
    legibility = "High" if len(ocr_text) > 100 else "Low"
    
    has_scale = "Verified" if any(re.search(r"SCALE:?\s*\d+:\d+", l, re.I) for l in ocr_text.splitlines()) else "Undetected"
    scale_text = "Undetected"
    scale_match = re.search(r"SCALE:?\s*(\d+:\d+)", ocr_text, re.I)
    if scale_match:
        scale_text = f"Verified ({scale_match.group(1)})"

    # 3. Suitability Assessment
    conf_score = 0.5 # Default
    if len(ocr_text) > 500: conf_score += 0.2
    if has_scale == "Verified": conf_score += 0.15
    if drawing_type == "ARCHITECTURAL_LAYOUT": conf_score += 0.1
    
    suitability = "MANUAL_INTERVENTION"
    if conf_score > 0.8:
        suitability = "AUTOMATED_ESTIMATION"
    elif conf_score > 0.6:
        suitability = "PARTIAL_AUTOMATION"
        
    readiness = "READY_FOR_INTERPRETATION" if conf_score > 0.7 else "NOT_READY"

    # 4. Drivers and Triggers
    drivers = []
    if has_scale == "Verified": drivers.append("EXPLICIT_SCALE")
    if len(re.findall(r"\d+\.?\d*m", ocr_text)) > 5: drivers.append("EXPLICIT_DIMENSIONING")
    if drawing_type != "GENERAL_ARRANGEMENT": drivers.append("STANDARDIZED_DRAWING_TYPE")

    blockers = "None"
    if conf_score < 0.5: blockers = "Low OCR Quality / Sparse Text"
    
    verifications = []
    if has_scale == "Undetected": verifications.append("Manual scale calibration")
    if "structural" in drawing_type.lower(): verifications.append("Structural reinforcement detail validation")

    # 5. Recommendation
    recommendation = "EXECUTE_HYBRID_ESTIMATION_WORKFLOW"
    if suitability == "AUTOMATED_ESTIMATION":
        recommendation = "PROCEED_TO_FULL_AUTOMATION"

    return PlanClassificationReport(
        metadata=DrawingMetadata_Custom(
            drawing_title=drawing_title,
            drawing_type=drawing_type,
            status="ANALYZED"
        ),
        analysis_parameters=SuitabilityScore(
            suitability=suitability,
            confidence_score=round(conf_score, 2),
            engineering_readiness=readiness
        ),
        visual_cues_detection=VisualCues(
            geometry="Orthogonal" if "Layout" in drawing_title else "Variable",
            dimensions="Explicit / Multi-axis" if "EXPLICIT_DIMENSIONING" in drivers else "Partial",
            scale=scale_text,
            annotations="Clear" if legibility == "High" else "Sparse",
            legibility=legibility
        ),
        suitability_drivers=drivers,
        intervention_triggers=InterventionTriggers(
            automation_blockers=blockers,
            verification_required=verifications
        ),
        automation_recommendation=recommendation
    )
