"""
Verification test for Narrative Intelligence Layer (Phase 8.1)
"""
from services.narrative_service import generate_narrative_report

print("="*70)
print("TEST: Narrative Intelligence (BOQ Report)")
print("="*70)

# SCENARIO: Complete Project Data
full_payload = {
    # Readiness/Confidence Data
    "readiness_status": "READY",
    "readiness_score": 0.88,
    "confidence_level": "High",
    "risks": [],
    "warnings": [],
    "assumptions": ["Used default Uganda brick size (200x100x100mm)"],
    
    # Cost Data
    "currency": "UGX",
    "total_project_cost": 4500000.0,
    "line_items": [
        {"item": "Burnt Clay Bricks", "quantity": 5000, "unit": "pcs", "rate": 400, "amount": 2000000},
        {"item": "Cement (50kg)", "quantity": 25, "unit": "bags", "rate": 35000, "amount": 875000},
        {"item": "Lake Sand", "quantity": 7, "unit": "tons", "rate": 60000, "amount": 420000}
    ],
    
    # Wall Data
    "walls": [
        {"label": "Wall A", "length_m": 5.0, "area_sqm": 15.0},
        {"label": "Wall B", "length_m": 4.0, "area_sqm": 12.0}
    ]
}

print("\n--- Generating Report ---")
report = generate_narrative_report(full_payload)
print(report)

print("-" * 30)
# Verification Checks
required_sections = [
    "FINAL BOQ INTELLIGENCE REPORT",
    "SECTION 1: PROJECT OVERVIEW",
    "SECTION 2: QUANTITY SUMMARY",
    "SECTION 3: COST BREAKDOWN",
    "SECTION 4: ASSUMPTIONS",
    "SECTION 5: RISK",
    "SECTION 6: PROFESSIONAL DISCLAIMER",
    "4,500,000", # Cost check
    "High (Score: 0.88)" # Confidence check
]

missing = [s for s in required_sections if s not in report]

if not missing:
    print("\n[PASS] All sections and key data points present.")
else:
    print(f"\n[FAIL] Missing sections/data: {missing}")
