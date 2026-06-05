"""
Verification test for Pipeline Orchestrator (Phase 8.2)
"""
from services.orchestrator_service import generate_pipeline_status_report

print("="*70)
print("TEST: Pipeline Orchestration Report")
print("="*70)

# SCENARIO: Partial Readiness Project
payload = {
    # Phase 6 & 7.5
    "ocr_text": "Wall A... Wall B...",
    "walls": [{"label": "A", "area_sqm": 10}, {"label": "B", "area_sqm": 12}],
    
    # Phase 7.6
    "total_project_cost": 2500000.0,
    "line_items": [{"item": "Brick", "quantity": 1000}],
    
    # Phase 8.0 (Review)
    "readiness_status": "PARTIAL",
    "confidence_score": 0.65,
    "warnings": ["Low OCR confidence"],
    "assumptions": ["Assumed Wall Height 3.0m"],
    "risks": ["Verification needed"]
}

print("\n--- Generating Report ---")
report = generate_pipeline_status_report(payload)
print(report)

print("-" * 30)

# Verification Logic
required_sections = [
    "END-TO-END PIPELINE STATUS REPORT",
    "SECTION 1: PIPELINE OVERVIEW",
    "SECTION 2: PHASE EXECUTION STATUS",
    "Phase 7.6 (Cost Estimation):         Completed",
    "SECTION 3: DATA CONTINUITY CHECK",
    "SECTION 4: FITNESS FOR USE ASSESSMENT",
    "Requires Professional Verification Before Use", # Matches PARTIAL status
    "SECTION 5: SYSTEM CONFIDENCE SYNTHESIS",
    "SECTION 6: RECOMMENDED NEXT ACTIONS"
]

missing = [s for s in required_sections if s not in report]

if not missing:
    print("\n[PASS] All sections and status logic verified.")
else:
    print(f"\n[FAIL] Missing sections/logic: {missing}")
