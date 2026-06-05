from typing import Dict, Any, List

def generate_pipeline_status_report(data: Dict[str, Any]) -> str:
    """
    Generates an End-to-End Pipeline Status Report.
    Acts as an Orchestrator view of the entire estimation process.
    
    Structure:
    1. Pipeline Overview
    2. Phase Execution Status
    3. Data Continuity Check
    4. Fitness for Use Assessment
    5. System Confidence Synthesis
    6. Recommended Next Actions
    """
    
    # --- Extract Data Signals ---
    # Input/Interpretation (Phase 6.x)
    ocr_text = data.get("ocr_text", "")
    walls = data.get("walls", [])
    has_ocr = len(ocr_text) > 50
    has_walls = len(walls) > 0
    
    # Quantification (Phase 7.5)
    total_area = sum(w.get("area_sqm", 0) for w in walls)
    has_quantities = total_area > 0
    
    # Costing (Phase 7.6)
    total_cost = data.get("total_project_cost", 0.0)
    line_items = data.get("line_items", [])
    has_cost = total_cost > 0
    
    # Confidence/Readiness (Phase 7.9/8.0)
    conf_score = data.get("confidence_score", 0.0)
    readiness_status = data.get("readiness_status", "UNKNOWN") # READY, PARTIAL, NOT_READY
    warnings = data.get("warnings", [])
    assumptions = data.get("assumptions", [])
    risks = data.get("risks", [])
    
    lines = []
    
    # --- SECTION 1: PIPELINE OVERVIEW ---
    lines.append("END-TO-END PIPELINE STATUS REPORT")
    lines.append("=================================\n")
    
    lines.append("SECTION 1: PIPELINE OVERVIEW")
    lines.append("-" * 30)
    lines.append("The estimation pipeline processed architectural inputs through OCR extraction,")
    lines.append("semantic interpretation, automated quantification, cost analysis, and")
    lines.append("risk assessment layers to produce the final project intelligence.")
    lines.append("")

    # --- SECTION 2: PHASE EXECUTION STATUS ---
    lines.append("SECTION 2: PHASE EXECUTION STATUS")
    lines.append("-" * 30)
    
    # Phase 6.x
    p6_status = "Completed" if has_walls and has_ocr else "Partial" if has_walls else "Missing"
    lines.append(f"- Phase 6.x (Input Interpretation):   {p6_status}")
    if has_walls:
        lines.append(f"  > Detected {len(walls)} wall segments from input.")
    else:
        lines.append(f"  > Failed to interpret valid wall geometry.")

    # Phase 7.5
    p75_status = "Completed" if has_quantities else "Skipped"
    lines.append(f"- Phase 7.5 (Material Quantification): {p75_status}")
    if has_quantities:
        lines.append(f"  > Calculated physical quantities (Area/Volume).")
        
    # Phase 7.6
    p76_status = "Completed" if has_cost else "Pending"
    lines.append(f"- Phase 7.6 (Cost Estimation):         {p76_status}")
    if has_cost:
        lines.append(f"  > Generated financial breakdown for {len(line_items)} items.")
        
    # Phase 7.7
    p77_status = "Available" if has_cost else "Unavailable"
    lines.append(f"- Phase 7.7 (BOQ Structuring):         {p77_status}")
    
    # Phase 8.0
    p80_status = "Completed" if readiness_status != "UNKNOWN" else "Pending"
    lines.append(f"- Phase 8.0 (Confidence & Risk):       {p80_status}")
    if p80_status == "Completed":
        lines.append(f"  > Rated Project Readiness as '{readiness_status}'.")
        
    lines.append("")

    # --- SECTION 3: DATA CONTINUITY CHECK ---
    lines.append("SECTION 3: DATA CONTINUITY CHECK")
    lines.append("-" * 30)
    
    continuity_issues = []
    if not has_ocr: continuity_issues.append("Weak input signal (OCR text sparse).")
    if has_ocr and not has_walls: continuity_issues.append("Input text exists but interpretation failed to extract geometry.")
    if has_walls and not has_cost: continuity_issues.append("Quantities exist but cost rates were not applied.")
    
    if not continuity_issues:
        lines.append("Pipeline Continuity: STRONG. All downstream phases received valid inputs.")
    else:
        lines.append("Pipeline Continuity: COMMPROMISED. Gaps detected:")
        for issue in continuity_issues:
            lines.append(f"- {issue}")
            
    if assumptions:
        lines.append("\nAssumption Reliability:")
        lines.append(f"- System relied on defaults for: {', '.join(assumptions[:3])}...")
    
    lines.append("")

    # --- SECTION 4: FITNESS FOR USE ASSESSMENT ---
    lines.append("SECTION 4: FITNESS FOR USE ASSESSMENT")
    lines.append("-" * 30)
    
    fitness = "Not Fit for Decision-Making"
    reason = "Critical data missing."
    
    if readiness_status == "READY":
        fitness = "Suitable for Budgeting & Planning"
        reason = "High confidence data with complete cost breakdown."
    elif readiness_status == "PARTIAL":
        fitness = "Requires Professional Verification Before Use"
        reason = "Valid estimates produced but relies on significant assumptions."
    elif readiness_status == "NOT_READY":
        fitness = "Not Fit for Decision-Making"
        reason = "Low confidence or missing structural data."
        
    lines.append(f"Assessment: {fitness}")
    lines.append(f"Justification: {reason}")
    lines.append("")

    # --- SECTION 5: SYSTEM CONFIDENCE SYNTHESIS ---
    lines.append("SECTION 5: SYSTEM CONFIDENCE SYNTHESIS")
    lines.append("-" * 30)
    
    lines.append(f"Composite Confidence Score: {conf_score:.2f} / 1.00")
    
    if conf_score >= 0.8:
        lines.append("Synthesis: Excellent data integrity. The system has high trust in the generated outputs.")
    elif conf_score >= 0.5:
        lines.append("Synthesis: Moderate data integrity. The outputs are mathematically correct but depend on unverified inputs.")
    else:
        lines.append("Synthesis: Low data integrity. The inputs were ambiguous, leading to speculative outputs.")
        
    if warnings:
        lines.append(f"System Warnings: {len(warnings)} reported signal issues.")
    lines.append("")

    # --- SECTION 6: RECOMMENDED NEXT ACTIONS ---
    lines.append("SECTION 6: RECOMMENDED NEXT ACTIONS")
    lines.append("-" * 30)
    
    actions = []
    if readiness_status == "READY":
        actions.append("Proceed to detailed tender documentation.")
        actions.append("Export PDF BOQ for client review.")
    elif readiness_status == "PARTIAL":
        actions.append("Verify wall heights and dimensions on site.")
        actions.append("Confirm key material rates (Cement/Sand) with local suppliers.")
        actions.append("Review assumed structural elements.")
    else:
        actions.append("Upload higher resolution architectural drawings.")
        actions.append("Provide explicit scale and dimension text.")
        actions.append("Manual quantity takeoff required.")
        
    for i, action in enumerate(actions, 1):
        lines.append(f"{i}. {action}")
        
    lines.append("\n[END OF PIPELINE REPORT]")
    
    return "\n".join(lines)
