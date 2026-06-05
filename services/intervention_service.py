from typing import List, Dict, Any
from schemas.intervention import InterventionAnalysis, InterventionAnalysisResponse, HumanInputRequirement

def analyze_intervention_needs(
    confidence: float,
    ocr_quality: Dict[str, Any],
    measurements: List[Any],
    readiness: str,
    path_decision: str
) -> InterventionAnalysisResponse:
    """
    Supervisory logic to determine exactly what human input is needed for data safety.
    """
    intervention_required = False
    required_inputs = []
    automation_allowed = ["Geometric normalization", "Standard height application"]
    
    # 1. Human Intervention Triggers
    
    # Case: Low confidence or Manual-First path
    if confidence < 0.4 or path_decision == "MANUAL_FIRST":
        intervention_required = True
        required_inputs.append(HumanInputRequirement(
            parameter="Primary Wall Dimensions",
            unit="mm",
            reason="OCR extraction density fell below professional safety thresholds."
        ))
    
    # Case: Weak OCR but potentially salvageable
    if ocr_quality.get("is_weak") and not ocr_quality.get("is_untrustworthy"):
        intervention_required = True
        required_inputs.append(HumanInputRequirement(
            parameter="Plan Scale",
            unit="ratio (e.g., 1:100)",
            reason="Textual scale annotations were unreadable. Required to calibrate vision-first measurements."
        ))
        
    # Case: Missing measurements
    if len(measurements) < 3:
        intervention_required = True
        required_inputs.append(HumanInputRequirement(
            parameter="Representative Longitudinal Dimension",
            unit="mm",
            reason="Insufficient ground-truth measurements found on plan to correlate vision data."
        ))
        
    # 2. Automation Allowed (What is still safe)
    if len(measurements) > 0:
        automation_allowed.append("Wall Segment detection")
        automation_allowed.append("Opening (Door/Window) spatial association")
        
    if readiness == "PARTIAL":
        automation_allowed.append("Preliminary Masonry Type mapping")

    # 3. Engineering Note
    if intervention_required:
        note = (
            "Professional accountability alert: The digital fidelity of the uploaded plan requires "
            "targeted human input to ensure quantity accuracy meets construction standards."
        )
    else:
        note = "Data quality is optimal. Full autonomous estimation is proceeding as sanctioned by the decision layer."

    analysis = InterventionAnalysis(
        intervention_required=intervention_required,
        required_inputs=required_inputs,
        automation_allowed=automation_allowed,
        engineering_note=note
    )
    
    return InterventionAnalysisResponse(intervention_analysis=analysis)
