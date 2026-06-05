"""
Verification test for Confidence Service (Phase 7.9) - Direct Service Test
"""
from services.confidence_service import analyze_estimation_confidence

print("="*70)
print("TEST: Confidence & Validation Logic (Direct)")
print("="*70)

# SCENARIO 1: High Confidence
high_conf_payload = {
    "ocr_text": "Wall A length 5m. Wall B length 4m. Wall C length 3m. Scale 1:100 verified.",
    "walls": [
        {"label": "Wall A", "length_m": 5.0},
        {"label": "Wall B", "length_m": 4.0},
        {"label": "Wall C", "length_m": 3.0},
        {"label": "Wall D", "length_m": 2.0},
        {"label": "Wall E", "length_m": 6.0}
    ],
    "custom_rates": {"brick_price": 500},
    "scale_provided": True
}

print("\n--- Test 1: High Confidence Scenario ---")
res1 = analyze_estimation_confidence(high_conf_payload)
print(f"Score: {res1.confidence_score} ({res1.confidence_level})")
print(f"Warnings: {res1.warnings}")

if res1.confidence_score >= 0.8:
    print("[PASS] Verified High Confidence Result")
else:
    print("[FAIL] Expected High Confidence")

# SCENARIO 2: Low Confidence
low_conf_payload = {
    "ocr_text": "Bad",
    "walls": [
        {"label": "Wall A", "length_m": 5.0} # Only 1 wall
    ],
    "custom_rates": None
}

print("\n--- Test 2: Low Confidence Scenario ---")
res2 = analyze_estimation_confidence(low_conf_payload)
print(f"Score: {res2.confidence_score} ({res2.confidence_level})")
print(f"Warnings: {res2.warnings}")
print(f"Assumptions: {res2.assumptions}")

# Expect penalties:
# Base 1.0
# Scan < 50 chars -> -0.15
# Wall count < 2 -> -0.1
# Expected <= 0.75

if res2.confidence_score < 0.8:
     print("[PASS] Verified Lower Confidence Result")
else:
     print("[FAIL] Expected Lower Confidence")
