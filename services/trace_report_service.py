from typing import List, Dict, Any
from schemas.trace_report import TraceReport, TraceReportResponse

def generate_pipeline_trace(
    ocr_raw: str,
    ocr_cleaned: str,
    measurements: List[Any],
    labels: List[Any],
    confidence: float,
    readiness: str,
    path_decision: str
) -> TraceReportResponse:
    """
    Generates a professional construction-grade audit report (Pipeline Trace).
    """
    # 1. Input Quality Summary
    ocr_len = len(ocr_cleaned)
    meas_count = len(measurements)
    quality_desc = "Standard image fidelity detected."
    if ocr_len < 200:
        quality_desc = "Weak OCR density detected. Textual data is insufficient for autonomous parsing."
    elif meas_count < 5:
        quality_desc = "Partial measurement density. Plan requires significant label correlation."
    
    input_summary = (
        f"The uploaded plan yielded {meas_count} discrete measurements via OCR parsing. "
        f"Data density is graded based on a cleaned character count of {ocr_len}. {quality_desc}"
    )

    # 2. Pipeline Decisions Taken
    decision_map = {
        "FULL_AUTOMATION": "System proceeded with Full Automation. High data fidelity enabled autonomous quantity take-off without manual intervention requirements.",
        "HYBRID": "System initiated a Hybrid Processing path. Geometric data was sufficient for extraction, but textual ambiguity necessitates human verification of material assignments.",
        "MANUAL_FIRST": "System defaulted to Manual-First mode. Data quality markers fell below safety thresholds, prioritizing professional oversight to prevent estimating errors."
    }
    decisions_taken = decision_map.get(path_decision, "System processed the plan through default safety heuristics.")

    # 3. Assumptions Applied
    assumptions = []
    assumptions.append("Standard Wall Height of 3.0m applied where vertical annotations were missing.")
    assumptions.append("Internal walls assumed non-load bearing unless thickness exceeded 200mm.")
    if meas_count > 0:
        assumptions.append("OCR labels correlated to geometric segments using 150px proximity threshold.")
    else:
        assumptions.append("All measurements assumed to be in millimeters (mm) per standard architectural convention.")

    # 4. Risks & Limitations
    risks = []
    if confidence < 0.3:
        risks.append("CRITICAL: Low data confidence ( < 30% ). High risk of dimension fabrication.")
    elif confidence < 0.6:
        risks.append("MODERATE: Potential label mis-alignment on complex plan intersections.")
    
    if "UNCLEAR" in ocr_raw.upper() or "LOW_QUALITY" in ocr_raw.upper():
        risks.append("SOURCE RISK: Plan contains explicit 'Unclear' or 'Low Quality' annotations.")
    
    risks.append("Limitation: System currently ignores structural reinforcement schedules.")

    # 5. Recommendation
    if path_decision == "FULL_AUTOMATION" and confidence >= 0.8:
        recommendation = "PROCEED. Quantities are ready for final BOQ generation with standard spot-checks."
    elif path_decision == "HYBRID" or (0.4 <= confidence < 0.8):
        recommendation = "VERIFY. Quantities require professional QS review against original source drawings before tendering."
    else:
        recommendation = "RE-MEASURE. Inadequate digital fidelity for reliable estimation. Manual measuring or re-upload of high-resolution plan required."

    report = TraceReport(
        input_quality_summary=input_summary,
        pipeline_decisions_taken=decisions_taken,
        assumptions_applied=assumptions,
        risks_and_limitations=risks,
        recommendation=recommendation
    )
    
    return TraceReportResponse(trace_report=report)
