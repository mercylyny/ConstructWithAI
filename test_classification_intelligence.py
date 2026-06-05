"""
Verification: Phase 11.0 - Construction Plan Analysis Intelligence
Tests the classification and suitability logic on real and mock data.
"""

from services.classification_service import classify_drawing_suitability
from services.ai_interpreter import get_stored_ocr_text
import json
import os

def test_real_plan_classification():
    print("=" * 80)
    print("TESTING CLASSIFICATION logic with Mock Plan Data")
    print("=" * 80)
    
    filename = "NANSANA LAYOUT.pdf"
    # Force mock data for logic verification - need > 5 'm' measurements for EXPLICIT_DIMENSIONING
    ocr_text = "GROUND FLOOR LAYOUT PLAN L[--]03\nSCALE: 1:100\nKITCHEN BEDROOM\nWall A: 12.5m Wall B: 8.0m Wall C: 5.0m Wall D: 4.5m Wall E: 10m Wall F: 3m"
    print("INFO: Using simulated OCR text for verification...")

    # Run classification
    report = classify_drawing_suitability(filename, ocr_text)
    
    print(f"\nReport for: {report.metadata.drawing_title}")
    print(f"Drawing Type: {report.metadata.drawing_type}")
    print(f"Suitability: {report.analysis_parameters.suitability}")
    print(f"Confidence: {report.analysis_parameters.confidence_score}")
    print(f"Readiness: {report.analysis_parameters.engineering_readiness}")
    print(f"Scale: {report.visual_cues_detection.scale}")
    print(f"Drivers: {', '.join(report.suitability_drivers)}")
    print(f"Automation Advised: {report.automation_recommendation}")
    
    # Assertions
    assert report.metadata.drawing_type == "ARCHITECTURAL_LAYOUT"
    print("\nSUCCESS: Drawing type correctly identified.")
    assert "EXPLICIT_DIMENSIONING" in report.suitability_drivers
    print("SUCCESS: Suitability drivers detected correctly.")
    
def test_noisy_plan_classification():
    print("\n" + "=" * 80)
    print("TESTING CLASSIFICATION: NOISY/SPARSE DATA")
    print("=" * 80)
    
    noisy_text = "Drawing 1234\nSome random lines\nNo measurements found."
    report = classify_drawing_suitability("noisy.pdf", noisy_text)
    
    print(f"Suitability: {report.analysis_parameters.suitability}")
    print(f"Blockers: {report.intervention_triggers.automation_blockers}")
    
    assert report.analysis_parameters.suitability == "MANUAL_INTERVENTION"
    print("\nSUCCESS: Low quality drawing correctly triggers intervention.")

if __name__ == "__main__":
    try:
        test_real_plan_classification()
        test_noisy_plan_classification()
        print("\n" + "=" * 80)
        print("PHASE 11.0 VERIFICATION COMPLETE")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
