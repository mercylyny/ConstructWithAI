from typing import Dict, Any, List

def generate_narrative_report(data: Dict[str, Any]) -> str:
    """
    Phase 8.1: Narrative Intelligence
    Generates a professional construction narrative report (BOQ Intelligence)
    based on the provided estimation and execution data.
    """
    
    # --- Extract Data ---
    status = data.get("readiness_status", "UNKNOWN")
    score = data.get("readiness_score", data.get("confidence_score", 0.0))
    total_cost = data.get("total_project_cost", 0.0)
    currency = data.get("currency", "UGX")
    walls = data.get("walls", [])
    line_items = data.get("line_items", [])
    assumptions = data.get("assumptions", []) # Could be string or list of dicts
    evidence_data = data.get("evidence", {})
    failures = data.get("failures", [])
    risks = data.get("risks", [])
    
    lines = []
    
    # --- HEADER ---
    lines.append("FINAL PROFESSIONAL QUANTITY SURVEYING REPORT")
    lines.append("============================================\n")
    
    # --- SECTION 1: PROJECT OVERVIEW ---
    lines.append("SECTION 1: PROJECT OVERVIEW")
    lines.append("-" * 30)
    lines.append("This report presents a comprehensive construction estimation and Bill of Quantities (BOQ)")
    lines.append("derived through an automated AI pipeline. The scope covers masonry structural materials.")
    
    # Analyze sources from evidence or defaults
    sourcesUsed = []
    if evidence_data:
        sourcesUsed.append("Automated OCR extraction")
        sourcesUsed.append("Semantic Interpretation")
    else:
        sourcesUsed.append("Manual inputs")
    sourcesUsed.append("Engineering Algorithms & System Defaults")
    lines.append(f"Data Sources: {', '.join(sourcesUsed)}.")
    lines.append("")
    
    # --- SECTION 2: BILL OF QUANTITIES SUMMARY ---
    lines.append("SECTION 2: BILL OF QUANTITIES SUMMARY")
    lines.append("-" * 30)
    if not line_items:
        lines.append("No cost or material items generated.")
    else:
        for item in line_items:
            name = item.get("item", "Unknown Item")
            qty = item.get("quantity", 0)
            unit = item.get("unit", "")
            rate = item.get("rate", 0)
            amt = item.get("amount", 0)
            lines.append(f"- {name:<25} : {qty:>8,.1f} {unit:<5} @ {rate:>8,.0f} = {amt:>10,.0f} {currency}")
            
    lines.append("-" * 60)
    lines.append(f"TOTAL PROJECT ESTIMATE:       {currency} {total_cost:,.0f}")
    lines.append("")

    # --- SECTION 3: ENGINEERING ASSUMPTIONS ---
    lines.append("SECTION 3: ENGINEERING ASSUMPTIONS")
    lines.append("-" * 30)
    if assumptions:
        for asm in assumptions:
            if isinstance(asm, dict):
                # Using the Registry Engine schema format
                name = asm.get("name", "Unknown Parameter")
                val = asm.get("value", "")
                unit = asm.get("unit", "")
                reason = asm.get("reason", "")
                lines.append(f"- {name}: {val} {unit}")
                lines.append(f"  Justification: {reason}")
            else:
                lines.append(f"- {asm}")
    else:
        lines.append("- Standard construction estimation parameters (e.g., 10-15% wastage, 1:4 mortar ratio) applied.")
        lines.append("- Standard UGX prevailing market rates implemented as baseline overrides.")
    lines.append("")

    # --- SECTION 4: DATA QUALITY & EVIDENCE ---
    lines.append("SECTION 4: DATA QUALITY & EVIDENCE")
    lines.append("-" * 30)
    evidence_list = evidence_data.get("attributed_values", []) if isinstance(evidence_data, dict) else evidence_data
    if evidence_list and isinstance(evidence_list, list):
        for ev in evidence_list:
            if isinstance(ev, dict):
                name = ev.get("name", "Parameter")
                src = ev.get("source", "UNKNOWN")
                lines.append(f"- {name} established via {src}.")
    else:
        lines.append("The current run relies heavily on default mathematical heuristics.")
    lines.append(f"Cumulative Evidence Confidence Score: {score:.2f}/1.0")
    lines.append("")

    # --- SECTION 5: FAILURE & RISK ANALYSIS ---
    lines.append("SECTION 5: FAILURE & RISK ANALYSIS")
    lines.append("-" * 30)
    if failures:
        lines.append("The Failure Analysis Engine identified the following anomalies:")
        for f in failures:
            cat = f.get("category", "SYSTEM_WARNING")
            cause = f.get("root_cause", "")
            sev = f.get("severity", "MEDIUM")
            lines.append(f"[{sev}] {cat}: {cause}")
    elif risks:
        for r in risks:
             lines.append(f"- {r}")
    else:
        lines.append("No critical pipeline failures or missing data issues detected.")
    
    if score < 0.6:
         lines.append("\nWARNING: Low confidence limitations observed. Extensive manual data provision required.")
    lines.append("")

    # --- SECTION 6: PROFESSIONAL RECOMMENDATION ---
    lines.append("SECTION 6: PROFESSIONAL RECOMMENDATION")
    lines.append("-" * 30)
    if failures and any(f.get("severity") == "HIGH" for f in failures):
         lines.append("Recommendation: REDESIGN / RE-INPUT REQUIRED")
         lines.append("-> Critical missing data or OCR failures prevented an accurate estimate.")
         lines.append("-> Please supply missing parameters such as clear dimensions or verify annotations via RFI.")
    elif score < 0.8:
         lines.append("Recommendation: VERIFY")
         lines.append("-> System health is degraded. Verify assumed quantities prior to committing to procurement.")
    else:
         lines.append("Recommendation: PROCEED")
         lines.append("-> Estimate demonstrates high confidence and robust derivation. Suitable for budgetary approvals.")
    lines.append("")

    # --- SECTION 7: DISCLAIMER ---
    lines.append("SECTION 7: DISCLAIMER")
    lines.append("-" * 30)
    lines.append("This Bill of Quantities is an AI-assisted construction estimate generated")
    lines.append("based on the provided input documentation. While derived from standard")
    lines.append("engineering equations:")
    lines.append("1. Final construction quantities and assumptions must be verified by a licensed professional.")
    lines.append("2. Actual site conditions, wastages, and spot market rates may deviate heavily.")
    lines.append("3. This document is strictly for Planning and Preliminary Costing purposes only.")
    lines.append("\n[END OF REPORT]")
    
    return "\n".join(lines)
