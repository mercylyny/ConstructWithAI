from schemas.failure_analysis import FailureAnalysisRequest, FailureAnalysisResponse, FailureItem

def analyze_pipeline_failures(request: FailureAnalysisRequest) -> FailureAnalysisResponse:
    """
    Phase 19.0: Construction Failure Analysis Engine
    Categorizes anomalies from pipeline logs, missing values, and evidence attribution
    into actionable insights for human reviewers.
    """
    failures = []
    health = "HEALTHY"
    
    # 1. Check OCR Output & Document Quality
    if not request.ocr_output or len(request.ocr_output.strip()) < 15:
        failures.append(FailureItem(
            stage="Data Extraction",
            category="DOC_QUALITY",
            root_cause="OCR extraction returned minimal or no text, indicating a poor drawing scan.",
            severity="HIGH",
            human_action_required=True,
            recommended_fix="Request original vector PDF or higher quality scan from the architect."
        ))
        
    # 2. Check Pipeline Execution Logs for errors
    failed_steps = [log for log in request.pipeline_logs if "error" in log.lower() or "fail" in log.lower()]
    for err in failed_steps:
        failures.append(FailureItem(
            stage="Pipeline Execution",
            category="PIPELINE_ERROR",
            root_cause=f"System error detected: {err}",
            severity="HIGH",
            human_action_required=True,
            recommended_fix="Review backend system logs or restart the processing job."
        ))

    # 3. Check Confidence Scores
    for metric, score in request.confidence_scores.items():
        if score < 0.65:
            failures.append(FailureItem(
                stage="AI Inference",
                category="AI_CONFIDENCE",
                root_cause=f"Confidence for '{metric}' is critically low ({score:.2f}).",
                severity="MEDIUM",
                human_action_required=True,
                recommended_fix="Manual verification of extracted values required."
            ))
            
    # 4. Handle Missing Values
    if request.missing_values:
        missing_str = ", ".join(request.missing_values)
        severity = "HIGH" if "wall_height" in request.missing_values or "scale" in request.missing_values else "MEDIUM"
        failures.append(FailureItem(
            stage="Quantity Takeoff",
            category="MISSING_DATA",
            root_cause=f"Critical design parameters are missing: {missing_str}.",
            severity=severity,
            human_action_required=True,
            recommended_fix="Apply standard engineering assumptions or generate an RFI."
        ))

    # 5. Check Evidence Results
    if "unattributed_values" in request.evidence_results and request.evidence_results["unattributed_values"]:
        failures.append(FailureItem(
            stage="Attribution",
            category="HUMAN_REQUIRED",
            root_cause=f"{len(request.evidence_results['unattributed_values'])} BOQ values lack direct source attribution.",
            severity="MEDIUM",
            human_action_required=True,
            recommended_fix="Assign human review to validate these orphaned items."
        ))

    # Calculate Overall Project Health based on severities
    if any(f.severity == "HIGH" for f in failures):
        health = "NOT_READY"
    elif any(f.severity == "MEDIUM" for f in failures):
        health = "DEGRADED"
        
    summary = (
        "Construction Pipeline Analysis Complete. "
        "The system has protected against downstream engineering errors by conservatively raising anomalies. "
        f"{len(failures)} action items require technical review."
    )
    if not failures:
        summary = "No anomalous pipeline behavior detected. Output is verified and healthy for downstream estimation."

    return FailureAnalysisResponse(
        failures=failures,
        overall_system_health=health,
        engineering_summary=summary
    )
