"""
Verification: Phase 18.0 - Engineering Evidence Attribution Engine
Tests professional traceability for construction values.
"""

import json
from services.attribution_service import attribute_engineering_evidence

def test_evidence_attribution():
    print("=" * 80)
    print("TESTING ENGINEERING EVIDENCE ATTRIBUTION")
    print("=" * 80)
    
    quantities = [
        {
            "name": "Wall A Length",
            "value": 4500.0,
            "unit": "mm",
            "ocr_snippet": "Wall A: 4500",
            "confidence": 0.95
        },
        {
            "name": "Wall Height",
            "value": 3000.0,
            "unit": "mm"
            # No ocr_snippet -> Should fall back to ASSUMPTION
        },
        {
            "name": "Partition Thickness",
            "value": 115.0,
            "unit": "mm",
            "applied_rule": "Learned: Standard partition thickness for region"
        }
    ]
    
    overrides = {
        "Wall A Length": 4600.0 # Human correction
    }
    
    assumptions = [
        "Wall Height: Standard 3000mm default applied."
    ]
    
    print("\n--- Processing Attribution ---")
    result = attribute_engineering_evidence(quantities, "Plan raw text", assumptions, overrides)
    
    for val in result.attributed_values:
        print(f"\nValue: {val.name} = {val.value}{val.unit}")
        print(f"  Source: {val.source}")
        print(f"  Confidence: {val.confidence}")
        print(f"  Risk: {val.risk_flag}")
        for ev in val.evidence:
            print(f"  Evidence [{ev.type}]: {ev.reference}")

    # Validations
    v_map = {v.name: v for v in result.attributed_values}
    assert v_map["Wall A Length"].source == "HUMAN"
    assert v_map["Wall Height"].source == "ASSUMPTION"
    assert v_map["Wall Height"].risk_flag == "HIGH"
    assert v_map["Partition Thickness"].source == "LEARNED_RULE"
    
    # Save a sample result
    output_path = "evidence_attribution_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\n[SUCCESS] Results saved to {output_path}")

if __name__ == "__main__":
    try:
        test_evidence_attribution()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
