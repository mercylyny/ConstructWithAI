from typing import List, Dict, Any
from schemas.pipeline_decision import PipelineDecision, PipelineDecisionResponse, PipelineActions

def analyze_pipeline_path(
    ocr_raw: str, 
    ocr_cleaned: str, 
    measurements: List[Any], 
    labels: List[Any], 
    confidence: float
) -> PipelineDecisionResponse:
    """
    Decides the estimation path based on OCR quality, measurements found, and confidence.
    """
    risk_flags = []
    
    # 1. OCR Quality Assessment
    is_weak = len(ocr_cleaned) < 200
    is_incomplete = len(measurements) == 0
    failure_keywords = ["FAILED", "UNCLEAR", "LOW_QUALITY"]
    is_untrustworthy = any(kw in ocr_raw.upper() for kw in failure_keywords)
    
    if is_weak: risk_flags.append("LOW_OCR_QUALITY")
    if is_incomplete: risk_flags.append("MISSING_MEASUREMENTS")
    
    # 2. Confidence Interpretation
    if confidence < 0.30:
        conf_level = "LOW"
    elif 0.30 <= confidence <= 0.60:
        conf_level = "MEDIUM"
    else:
        conf_level = "HIGH"
        
    if conf_level == "LOW": risk_flags.append("LOW_CONFIDENCE")
    
    # 3. Pipeline Path Selection & Actions
    # Logic Order: MANUAL_FIRST (Checks if ANY safety trigger is met) -> FULL_AUTOMATION -> HYBRID
    
    if is_weak or is_untrustworthy or is_incomplete or confidence < 0.30:
        path = "MANUAL_FIRST"
        actions = PipelineActions(
            estimate_from_plan=False,
            estimate_from_ocr=False,
            manual_input_required=True,
            manual_verification_required=False,
            materials_detailed=False,
            cost_estimation=False,
            boq_reports=False
        )
        reasoning = "Insufficient OCR intelligence or low confidence detected. Switching to Manual-First mode for safety."
        
    elif not is_weak and not is_untrustworthy and not is_incomplete and confidence >= 0.60:
        path = "FULL_AUTOMATION"
        actions = PipelineActions(
            estimate_from_plan=True,
            estimate_from_ocr=True,
            manual_input_required=False,
            manual_verification_required=False,
            materials_detailed=True,
            cost_estimation=True,
            boq_reports=True
        )
        reasoning = "Sufficient plan intelligence detected for autonomous estimation."
        
    else:
        # Falls through to Hybrid if it has text but doesn't meet Full Automation criteria
        path = "HYBRID"
        actions = PipelineActions(
            estimate_from_plan=False,
            estimate_from_ocr=True,
            manual_input_required=False,
            manual_verification_required=True,
            materials_detailed=True,
            cost_estimation=True,
            boq_reports=True
        )
        reasoning = "Partial plan intelligence detected; human verification required to ensure accuracy."

    decision = PipelineDecision(
        path=path,
        confidence_level=conf_level,
        actions=actions,
        risk_flags=risk_flags,
        reasoning=reasoning
    )
    
    return PipelineDecisionResponse(pipeline_decision=decision)
