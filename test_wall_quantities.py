"""
Verification test for Phase 7.4: Automated Wall Quantity Calculation
"""
from services.wall_quantity_calculator import calculate_wall_quantities

# Test Data (Output from Phase 7.3.3)
test_walls = [
    {"label": "Wall A", "length_m": 4.5},
    {"label": "W2", "length_m": 3.6},
    {"label": "INT 1", "length_m": 2.4}
]
test_height = 3.0

print("="*70)
print("PHASE 7.4: WALL QUANTITY CALCULATION TEST")
print("="*70)

print("\nInput Data:")
print(f"Height: {test_height}m")
for w in test_walls:
    print(f"  - {w['label']}: {w['length_m']}m")

# Run Calculation
result = calculate_wall_quantities(test_walls, test_height)

print("\nCalculation Results:")
print("-"*50)
for w in result['walls']:
    print(f"Label: {w['label']}")
    print(f"  Length: {w['length_m']}m")
    print(f"  Height: {w['height_m']}m")
    print(f"  Thickness: {w['thickness_m']}m")
    print(f"  Area: {w['area_sqm']} sqm")
    print(f"  Volume: {w['volume_cum']} cum")
    print("")

print("-"*50)
print("Totals:")
print(f"Total Area: {result['totals']['total_wall_area_sqm']} sqm")
print(f"Total Volume: {result['totals']['total_wall_volume_cum']} cum")

# Verification Logic
expected_area_A = 4.5 * 3.0
expected_vol_A = expected_area_A * 0.20 # Default

expected_area_W2 = 3.6 * 3.0
expected_vol_W2 = expected_area_W2 * 0.20 # Default

expected_area_INT = 2.4 * 3.0
expected_vol_INT = expected_area_INT * 0.15 # Partition

print("\nVerification Checks:")
checks = [
    (result['walls'][0]['volume_cum'] == round(expected_vol_A, 2), "Wall A volume correct (0.2m thick)"),
    (result['walls'][2]['thickness_m'] == 0.15, "INT 1 thickness is 0.15m"),
    (result['totals']['total_wall_area_sqm'] > 0, "Total area calculated")
]

all_passed = True
for passed, msg in checks:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {msg}")
    if not passed:
        all_passed = False

if all_passed:
    print("\n✅ SUCCESS: Wall quantity calculation verified.")
else:
    print("\n❌ FAILURE: Verification failed.")
