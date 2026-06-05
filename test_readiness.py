"""
Verification test for Project Readiness Layer (Phase 8.0)
"""
from services.readiness_service import analyze_project_readiness

print("="*70)
print("TEST: Project Readiness & Risk Intelligence")
print("="*70)

# SCENARIO 1: READY
# High confidence, costs present, quantities present
ready_payload = {
    "confidence_score": 0.95,
    "confidence_level": "High",
    "warnings": [],
    "assumptions": ["Minor assumption"],
    "total_project_cost": 5000000.0,
    "walls": [{"label": "A", "length": 5}],
    "line_items": [{"item": "Steel Bars", "amount": 1000}, {"item": "Bricks", "amount": 4000}], # Contains Steel
    "ocr_text": "Complete plan text..."
}

print("\n--- Test 1: READY Scenario ---")
res1 = analyze_project_readiness(ready_payload)
print(f"Status: {res1.readiness_status}")
print(f"Score:  {res1.readiness_score}")
print(f"Risks:  {res1.risks}")
print(f"Summary: {res1.summary}")

if res1.readiness_status == "READY" and res1.readiness_score >= 0.75:
    print("[PASS] Verified READY state")
else:
    print(f"[FAIL] Expected READY, got {res1.readiness_status}")


# SCENARIO 2: PARTIAL (Risk Detected)
# Medium confidence, Default parameters used, Missing Steel
partial_payload = {
    "confidence_score": 0.65,
    "confidence_level": "Medium",
    "warnings": ["Short OCR text"],
    "assumptions": ["Used assumed default wall height", "Using default market rates"],
    "total_project_cost": 2000000.0,
    "walls": [{"label": "A", "length": 5}],
    "line_items": [{"item": "Bricks", "amount": 2000}], # No Steel
    "ocr_text": "Short..."
}

print("\n--- Test 2: PARTIAL Scenario ---")
res2 = analyze_project_readiness(partial_payload)
print(f"Status: {res2.readiness_status}")
print(f"Score:  {res2.readiness_score}")
print(f"Risks:  {res2.risks}")
print(f"Checks: {res2.required_human_checks}")

# Expectations:
# Status: PARTIAL
# Risks: "Relied on Assumed Wall Heights", "Used Generic Market Rates", "No Structural/Steel Data Processed"

risk_str = str(res2.risks)
if res2.readiness_status == "PARTIAL":
    if "Assumed Wall Heights" in risk_str and "Reference" not in risk_str: # Checking risk substring presence
         print("[PASS] Verified PARTIAL state & Risk Detection")
    else:
         print(f"[FAIL] Risks missing. Got: {risk_str}")
else:
    print(f"[FAIL] Expected PARTIAL, got {res2.readiness_status}")


# SCENARIO 3: NOT READY
# Low confidence (0.3), No Cost
not_ready_payload = {
    "confidence_score": 0.3,
    "total_project_cost": 0.0,
    "walls": [],
    "ocr_text": ""
}

print("\n--- Test 3: NOT READY Scenario ---")
res3 = analyze_project_readiness(not_ready_payload)
print(f"Status: {res3.readiness_status}")
print(f"Score:  {res3.readiness_score}")
if res3.readiness_status == "NOT_READY":
    print("[PASS] Verified NOT_READY state")
else:
    print(f"[FAIL] Expected NOT_READY, got {res3.readiness_status}")
