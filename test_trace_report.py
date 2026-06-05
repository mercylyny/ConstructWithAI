"""
Verification: Phase 15.0 - Pipeline Trace Reporting
Tests the generation of professional construction audit reports.
"""

import json
from services.trace_report_service import generate_pipeline_trace

def test_trace_report():
    print("=" * 80)
    print("TESTING PIPELINE TRACE REPORTING")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Scenario A: High Quality Plan (Full Automation)",
            "ocr_raw": "Project X. Ground Floor Plan. Wall Dimensions: W1: 4500mm, W2: 3200mm.",
            "ocr_cleaned": "Project X. Ground Floor Plan. [Padding to exceed 200 chars] Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            "measurements": [4500, 3200, 1500, 2000, 3000, 4000],
            "labels": ["W1", "W2", "W3", "W4", "W5", "W6"],
            "confidence": 0.92,
            "readiness": "READY",
            "path_decision": "FULL_AUTOMATION"
        },
        {
            "name": "Scenario B: Weak OCR / Low Confidence (Re-measure)",
            "ocr_raw": "Draft plan copy.",
            "ocr_cleaned": "Draft plan copy.",
            "measurements": [],
            "labels": [],
            "confidence": 0.15,
            "readiness": "NOT_READY",
            "path_decision": "MANUAL_FIRST"
        }
    ]

    for s in scenarios:
        print(f"\n--- {s['name']} ---")
        result = generate_pipeline_trace(
            s['ocr_raw'], 
            s['ocr_cleaned'], 
            s['measurements'], 
            s['labels'], 
            s['confidence'],
            s['readiness'],
            s['path_decision']
        )
        report = result.trace_report
        print(f"Quality Summary: {report.input_quality_summary[:100]}...")
        print(f"Decisions: {report.pipeline_decisions_taken[:100]}...")
        print(f"Assumptions Count: {len(report.assumptions_applied)}")
        print(f"Risks/Limitations Count: {len(report.risks_and_limitations)}")
        print(f"Recommendation: {report.recommendation}")

        # Basic validations
        if s['path_decision'] == "FULL_AUTOMATION":
            assert "PROCEED" in report.recommendation
        else:
            assert "RE-MEASURE" in report.recommendation or "VERIFY" in report.recommendation

    # Save a sample result
    output_path = "pipeline_trace_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\n[SUCCESS] Results saved to {output_path}")

if __name__ == "__main__":
    try:
        test_trace_report()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
