"""
Verification test for Cost Estimation Layer (Phase 7.6)
"""
from services.cost_service import calculate_project_cost
from schemas.costing import CostEstimationRequest, MaterialQuantities, CustomRates

print("="*70)
print("TEST: Cost Estimation Layer (Uganda Context)")
print("="*70)

# Scenario: Small Room Project
# 2000 Bricks, 0.5 m3 Mortar
test_quantities = MaterialQuantities(
    total_bricks_count=2000,
    total_mortar_volume_m3=0.5
)

# 1. Default Prices Test
print("\n--- Test 1: Default Prices ---")
req_default = CostEstimationRequest(quantities=test_quantities)
res_default = calculate_project_cost(req_default)

for item in res_default.line_items:
    print(f"{item.item}: {item.quantity} {item.unit} @ {item.rate} = {item.amount:,.0f} UGX")

print(f"Total: {res_default.total_project_cost:,.0f} UGX")

# Verification logic (Defaults)
# Bricks: 2000 * 400 = 800,000
# Mortar: 0.5 m3
#   Cement: ceil(0.5 * 7) = 4 bags * 35,000 = 140,000
#   Sand: 0.5 * 1.2 = 0.6 tons * 60,000 = 36,000
# Total Expected: 976,000

expected_total = 976000
if abs(res_default.total_project_cost - expected_total) < 100:
    print("✅ Default pricing verification PASSED")
else:
    print(f"❌ Default pricing verification FAILED. Expected {expected_total}, Got {res_default.total_project_cost}")


# 2. Custom Rates Test
print("\n--- Test 2: Custom Rates Only ---")
custom_rates = CustomRates(brick_price_ugx=500.0) # Expensive bricks
req_custom = CostEstimationRequest(quantities=test_quantities, custom_rates=custom_rates)
res_custom = calculate_project_cost(req_custom)

# Verification logic (Custom)
# Bricks: 2000 * 500 = 1,000,000 (+200k from default)
# Others remain default (Cement 140k + Sand 36k) = 176k
# Total Expected: 1,176,000

expected_custom = 1176000
print(f"Total with custom bricks (500 UGX): {res_custom.total_project_cost:,.0f} UGX")

if abs(res_custom.total_project_cost - expected_custom) < 100:
    print("✅ Custom pricing verification PASSED")
else:
    print(f"❌ Custom pricing verification FAILED. Expected {expected_custom}, Got {res_custom.total_project_cost}")
