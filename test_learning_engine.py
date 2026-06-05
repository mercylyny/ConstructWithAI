"""
Verification: Phase 17.0 - AI Construction Learning Engine
Tests the extraction of rules from human corrections.
"""

import json
from services.learning_service import extract_learning_patterns

def test_learning_engine():
    print("=" * 80)
    print("TESTING AI CONSTRUCTION LEARNING ENGINE")
    print("=" * 80)
    
    # Mocked data reflecting a human audit
    original_ocr = "Plan Data: Wall L00mm. Wall 23Omm."
    corrections = {
        "ocr_text": {
            "L00": "100",  # Common L vs 1 error
            "23O": "230"   # Common O vs 0 error
        },
        "interpretation_deltas": [
            {
                "thickness": 100,
                "predicted": "PARTITION",
                "corrected": "LOAD_BEARING" # Deviant case for learning
            }
        ],
        "quantity_bias": 0.08 # Consistently 8% under in this region
    }
    building_context = {"type": "Industrial Warehouse", "region": "East Africa"}

    print("\n--- Processing Human Corrections ---")
    result = extract_learning_patterns(original_ocr, corrections, {}, building_context)
    analysis = result.learning_analysis
    
    print(f"Learned Rules Count: {len(analysis.learned_rules)}")
    for rule in analysis.learned_rules:
        print(f"  [{rule.scope}] Trigger: {rule.trigger_pattern} -> Action: {rule.action}")
    
    print(f"\nFuture Guidance (Auto-Apply): {analysis.future_guidance['auto_apply']}")
    print(f"Future Guidance (Require Human): {analysis.future_guidance['require_human']}")
    print(f"\nEngineering Note: {analysis.engineering_note}")

    # Validations
    assert len(analysis.learned_rules) >= 3, "Should have extracted multiple rules"
    assert any(r.scope == "OCR" for r in analysis.learned_rules)
    assert any(r.scope == "ESTIMATION" for r in analysis.learned_rules)
    
    # Save a sample result
    output_path = "learning_engine_result.json"
    with open(output_path, "w") as f:
        json.dump(result.dict(), f, indent=2)
    print(f"\n[SUCCESS] Results saved to {output_path}")

if __name__ == "__main__":
    try:
        test_learning_engine()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {str(e)}")
