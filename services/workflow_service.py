from schemas.workflow import WorkflowOrchestratorRequest, WorkflowOrchestratorResponse, WorkflowStep

def orchestrate_workflow(request: WorkflowOrchestratorRequest) -> WorkflowOrchestratorResponse:
    """
    Phase 21.0: Construction Workflow Orchestrator
    Determines the safest engineering pathway for generating a final BOQ.
    Strictly prevents automatic execution if data is missing or degraded.
    """
    failures = request.failures or []
    has_high_severity = any(f.get("severity") == "HIGH" for f in failures)
    data = request.available_data
    
    steps = []
    warnings = []
    
    # 1. Evaluate Data Safety & Confidence Rules
    # Rule 1: Never allow full automation if data is insufficient
    # Rule 2: Prefer safe engineering workflow over speed
    
    if request.confidence_score >= 0.85 and not has_high_severity and data.get("ocr", False) and data.get("assumptions", False):
        mode = "AUTOMATIC"
    elif request.confidence_score >= 0.60 and not has_high_severity:
        mode = "ASSISTED"
    else:
        # Fallback for ANY critical high severity errors or poor confidence
        mode = "MANUAL"
        
    # 2. Build Specific Steps based on Recommended Mode
    if mode == "AUTOMATIC":
        steps.append(WorkflowStep(
            step=1, 
            action="Generate Professional Estimation Report", 
            endpoint="/report/narrative", 
            required=True
        ))
        steps.append(WorkflowStep(
            step=2, 
            action="Export PDF Bill of Quantities", 
            endpoint="/report/boq/pdf", 
            required=False
        ))
        next_action = "Review the generated PDF compilation and proceed to procurement."
        
    elif mode == "ASSISTED":
        warnings.append("System confidence is moderate. Automated fallback defaults were utilized.")
        warnings.append("Professional validation of derived assumptions is strictly required.")
        
        steps.append(WorkflowStep(
            step=1, 
            action="Review Extracted Assumptions", 
            endpoint="/analyze/assumptions", 
            required=True
        ))
        steps.append(WorkflowStep(
            step=2, 
            action="Acknowledge Medium-Severity Warnings", 
            endpoint="/analyze/failures", 
            required=True
        ))
        steps.append(WorkflowStep(
            step=3, 
            action="Proceed to Estimation Report", 
            endpoint="/report/narrative", 
            required=False
        ))
        next_action = "Acknowledge the calculated assumptions. Complete the pipeline manually if confident."
        
    else:
        warnings.append("CRITICAL: Pipeline logic halted to prevent unsafe quantity estimation.")
        warnings.append("Insufficient data, illegible OCR, or critical pipeline failures detected.")
        
        steps.append(WorkflowStep(
            step=1, 
            action="Review Critical Failure Logs", 
            endpoint="/analyze/failures", 
            required=True
        ))
        steps.append(WorkflowStep(
            step=2, 
            action="Switch to Manual Takeoff Inputs", 
            endpoint="/attribute", 
            required=True
        ))
        steps.append(WorkflowStep(
            step=3, 
            action="Re-run Costing Engine", 
            endpoint="/estimate/costs", 
            required=True
        ))
        next_action = "Provide missing geometric overrides or initiate manual takeoff processes."

    return WorkflowOrchestratorResponse(
        recommended_mode=mode,
        steps=steps,
        warnings=warnings,
        next_action=next_action
    )
