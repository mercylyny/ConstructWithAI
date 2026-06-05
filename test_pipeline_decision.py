"""
Verification: Phase 14.0 - Pipeline Decision Intelligence
Tests different scenarios to verify path selection logic.
"""

import json
from services.pipeline_decision_service import analyze_pipeline_path

def test_pipeline_decision():
    print("=" * 80)
    print("TESTING PIPELINE DECISION INTELLIGENCE")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Scenario A: High Quality (Full Automation)",
            "ocr_raw": "Project ABC - Ground Floor. All dims in mm. Wall 1: 5000mm. Wall 2: 3000mm.",
            "ocr_cleaned": "Project ABC - Ground Floor. All dims in mm. Wall 1: 5000mm. Wall 2: 3000mm. [Extra padding to exceed 200 chars] Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
            "measurements": [5000, 3000],
            "labels": ["Wall 1", "Wall 2"],
            "confidence": 0.85,
            "expected_path": "FULL_AUTOMATION"
        },
        {
            "name": "Scenario B: WEAK OCR (Manual-First)",
            "ocr_raw": "Draft plan.",
            "ocr_cleaned": "Draft plan.",
            "measurements": [],
            "labels": [],
            "confidence": 0.2,
            "expected_path": "MANUAL_FIRST"
        },
        {
            "name": "Scenario C: Partial Measurements (Hybrid)",
            "ocr_raw": "Floor plan. Wall A: 4500. Other walls not annotated.",
            "ocr_cleaned": "Floor plan. Wall A: 4500. Other walls not annotated. [Padding] Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            "measurements": [4500],
            "labels": ["Wall A"],
            "confidence": 0.5,
            "expected_path": "HYBRID"
        },
        {
            "name": "Scenario D: LOW_QUALITY keyword (Manual-First)",
            "ocr_raw": "OCR RESULT: LOW_QUALITY. FAILED TO READ.",
            "ocr_cleaned": "OCR RESULT: LOW_QUALITY. FAILED TO READ. [Padding] Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.",
            "measurements": [1000],
            "labels": ["W1"],
            "confidence": 0.7, # High conf but untrustworthy text
            "expected_path": "MANUAL_FIRST"
        }
    ]

    for s in scenarios:
        print(f"\n--- {s['name']} ---")
        result = analyze_pipeline_path(
            s['ocr_raw'], 
            s['ocr_cleaned'], 
            s['measurements'], 
            s['labels'], 
            s['confidence']
        )
        decision = result.pipeline_decision
        print(f"Path: {decision.path} (Expected: {s['expected_path']})")
        print(f"Confidence Level: {decision.confidence_level}")
        print(f"Risk Flags: {decision.risk_flags}")
        print(f"Reasoning: {decision.reasoning}")
        
        assert decision.path == s['expected_path'], f"Failed {s['name']}"

    # Save a sample result
    output_path = "pipeline_decision_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\nSUCCESS: Results saved to {output_path}")

if __name__ == "__main__":
    try:
        test_pipeline_decision()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
