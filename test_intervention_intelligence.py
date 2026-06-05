"""
Verification: Phase 16.0 - Automated Intervention Intelligence
Tests the supervisor logic for requesting human inputs.
"""

import json
from services.intervention_service import analyze_intervention_needs

def test_intervention_intelligence():
    print("=" * 80)
    print("TESTING AUTOMATED INTERVENTION INTELLIGENCE")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Scenario A: Low Confidence / Weak OCR (Critical Intervention)",
            "confidence": 0.25,
            "ocr_quality": {"is_weak": True, "is_untrustworthy": False},
            "measurements": [],
            "readiness": "NOT_READY",
            "path_decision": "MANUAL_FIRST"
        },
        {
            "name": "Scenario B: High Quality (No Intervention)",
            "confidence": 0.85,
            "ocr_quality": {"is_weak": False, "is_untrustworthy": False},
            "measurements": [5000, 3000, 1500, 2000, 4000],
            "readiness": "READY",
            "path_decision": "FULL_AUTOMATION"
        },
        {
            "name": "Scenario C: Partial Measurements (Targeted Input)",
            "confidence": 0.55,
            "ocr_quality": {"is_weak": False, "is_untrustworthy": False},
            "measurements": [4500], # Too few
            "readiness": "PARTIAL",
            "path_decision": "HYBRID"
        }
    ]

    for s in scenarios:
        print(f"\n--- {s['name']} ---")
        result = analyze_intervention_needs(
            s['confidence'], 
            s['ocr_quality'], 
            s['measurements'], 
            s['readiness'],
            s['path_decision']
        )
        analysis = result.intervention_analysis
        print(f"Intervention Required: {analysis.intervention_required}")
        print(f"Required Inputs Count: {len(analysis.required_inputs)}")
        for req in analysis.required_inputs:
            print(f"  -> {req.parameter} ({req.unit}): {req.reason}")
        print(f"Automation Allowed: {analysis.automation_allowed}")
        print(f"Supervisor Note: {analysis.engineering_note[:100]}...")

        # Basic validations
        if s['path_decision'] == "MANUAL_FIRST" or len(s['measurements']) < 3:
            assert analysis.intervention_required == True, f"Failed {s['name']}: Should require intervention"
        elif s['path_decision'] == "FULL_AUTOMATION":
            assert analysis.intervention_required == False, f"Failed {s['name']}: Should NOT require intervention"

    # Save a sample result
    output_path = "intervention_analysis_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\n[SUCCESS] Results saved to {output_path}")

if __name__ == "__main__":
    try:
        test_intervention_intelligence()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
