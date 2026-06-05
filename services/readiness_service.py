from typing import List, Dict, Any
from pydantic import BaseModel

class ReadinessAssessment(BaseModel):
    readiness_status: str  # READY, PARTIAL, NOT_READY
    readiness_score: float # 0.0 - 1.0
    risks: List[str]
    recommendations: List[str]
    required_human_checks: List[str]
    summary: str
    
    # Phase 10.3: UX Contract
    intervention_needed: bool
    missing_critical_data: List[str]

def analyze_project_readiness(data: Dict[str, Any]) -> ReadinessAssessment:
    """
    Analyzes project data to determine if it is ready for execution.
    
    Expected Input Data (aggregated):
    - confidence_score: float (from Phase 7.9, 0.0-1.0)
    - confidence_level: str
    - warnings: List[str] (from confidence layer)
    - assumptions: List[str] (from confidence layer)
    - total_project_cost: float (from cost layer)
    - line_items: List (from cost layer)
    - ocr_text: str (raw text)
    - walls: List (detected walls)
    """
    
    # 1. Extract Core Signals
    conf_score = data.get("confidence_score", 0.0)
    warnings = data.get("warnings", [])
    assumptions = data.get("assumptions", [])
    total_cost = data.get("total_project_cost", 0.0)
    ocr_text = data.get("ocr_text", "")
    walls = data.get("walls", [])
    
    has_quantities = len(walls) > 0
    has_cost = total_cost > 0
    
    risks = []
    recommendations = []
    checks = []
    
    # 2. Risk Detection
    # R1: Confidence Risks
    if conf_score < 0.5:
        risks.append("Low AI Confidence Score (< 0.5)")
        recommendations.append("Review original plan image for clarity.")
    elif conf_score < 0.75:
        risks.append("Moderate AI Confidence")
        
    # R2: Missing Data
    if not has_quantities:
        risks.append("No Wall Quantities Detected")
        recommendations.append("Ensure plan has distinct wall lines and standard measurement labels.")
    
    if not has_cost:
        risks.append("No Cost Calculation Available")
        checks.append("Verify if material rates were applied.")
        
    # R3: Specific Warnings/Assumptions
    if "default height" in str(assumptions).lower() or "assumed" in str(assumptions).lower():
        risks.append("Relied on Assumed Wall Heights")
        checks.append("Verify wall heights on site (AI assumed default).")
        recommendations.append("Provide explicit wall height in inputs if known.")
        
    if "default market rates" in str(assumptions).lower():
        risks.append("Used Generic Market Rates")
        checks.append("Confirm current material prices with local supplier.")
        
    if len(warnings) > 2:
        risks.append("Multiple Analysis Warnings Detected")
        
    # R4: Structural Gaps (Heuristic)
    # If we have walls but no mention of "steel" or "foundation" in cost items (if cost line items details provided)
    line_items = data.get("line_items", [])
    item_names = [str(item.get("item", "")).lower() for item in line_items]
    if not any("steel" in x for x in item_names) and has_quantities:
        risks.append("No Structural/Steel Data Processed")
        checks.append("Structural engineering review required (Steel not estimated).")
        
    # 3. Determine Status & Score
    base_score = conf_score
    
    # Adjust base_score contextually for "Readiness" (which is stricter than just confidence)
    if not has_cost:
        base_score *= 0.8
    if not has_quantities:
        base_score *= 0.5
        
    final_score = round(base_score, 2)
    
    status = "NOT_READY"
    if final_score >= 0.75 and has_cost and has_quantities:
        status = "READY"
    elif final_score >= 0.45:
        status = "PARTIAL"
    else:
        status = "NOT_READY"
        
    # 4. Generate Summary
    if status == "READY":
        summary = f"Project appears ready for execution planning. Verified cost of {total_cost:,.0f} UGX with high confidence ({final_score})."
    elif status == "PARTIAL":
        summary = f"Project has valid data but requires verification. Identified {len(risks)} risks including: {risks[0] if risks else 'None'}. Review recommended."
    else:
        summary = "Project is NOT ready. foundational data or confidence is missing. extensive review or re-analysis required."
        
    # Phase 10.3: Determine Intervention Need
    intervention_needed = False
    missing_data = []
    
    if conf_score < 0.6:
        intervention_needed = True
        missing_data.append("Low Confidence")
        
    if not has_quantities:
         intervention_needed = True
         missing_data.append("Measurements")
         
    if not has_cost:
         intervention_needed = True
         missing_data.append("Cost Data")

    if status == "NOT_READY":
         intervention_needed = True
         
    return ReadinessAssessment(
        readiness_status=status,
        readiness_score=final_score,
        risks=risks,
        recommendations=recommendations,
        required_human_checks=checks,
        summary=summary,
        intervention_needed=intervention_needed,
        missing_critical_data=missing_data
    )
