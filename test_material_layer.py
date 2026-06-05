"""
Verification test for Detailed Material Estimation Layer
"""
from services.wall_material_service import estimate_wall_materials
from schemas.materials import WallSegment

print("="*70)
print("TEST: Detailed Wall Material Estimation")
print("="*70)

# Scenarios
# 1. Standard Wall: 4m long, 3m high, 230mm thick (2 layer), 2.0m2 opening
# 2. Partition Wall: 3m long, 3m high, 115mm thick (1 layer), 0m2 opening

test_walls = [
    WallSegment(
        wall_id="W1-Ext",
        length_m=4.0,
        height_m=3.0,
        thickness_mm=230.0,
        openings_area_m2=2.0
    ),
    WallSegment(
        wall_id="W2-Part",
        length_m=3.0,
        height_m=3.0,
        thickness_mm=115.0,
        openings_area_m2=0.0
    )
]

print(f"Input Walls: {len(test_walls)}")
for w in test_walls:
    print(f"  {w.wall_id}: {w.length_m}x{w.height_m}m, {w.thickness_mm}mm thick, -{w.openings_area_m2}m2 openings")

# Run calculation
result = estimate_wall_materials(test_walls)

print("\nResults:")
print("-" * 50)
for w in result.walls:
    print(f"Wall: {w.wall_id}")
    print(f"  Net Area: {w.net_area_m2} m2")
    print(f"  Bricks:   {w.total_bricks}")
    print(f"  Mortar:   {w.mortar_volume_m3} m3")

print("-" * 50)
print("Project Totals:")
print(f"  Total Bricks: {result.project_totals.total_bricks_count}")
print(f"  Total Mortar: {result.project_totals.total_mortar_volume_m3} m3")

# Manual Verification
# W1: Gross 12, Net 10. Thickness 230 (factor 2). 
# Bricks = 10 * 60 * 2 = 1200
# Mortar = 1.2 * 0.23 = 0.276

# W2: Gross 9, Net 9. Thickness 115 (factor 1).
# Bricks = 9 * 60 * 1 = 540
# Mortar = 0.54 * 0.23 = 0.1242

expected_w1_bricks = 1200
expected_w2_bricks = 540

print("\nValidation:")
w1_res = next(w for w in result.walls if w.wall_id == "W1-Ext")
w2_res = next(w for w in result.walls if w.wall_id == "W2-Part")

passed = True
if abs(w1_res.total_bricks - expected_w1_bricks) > 1:
    print(f"[FAIL] W1 Bricks: Got {w1_res.total_bricks}, Expected {expected_w1_bricks}")
    passed = False
else:
    print(f"[PASS] W1 Bricks correct ({expected_w1_bricks})")
    
if abs(w2_res.total_bricks - expected_w2_bricks) > 1:
    print(f"[FAIL] W2 Bricks: Got {w2_res.total_bricks}, Expected {expected_w2_bricks}")
    passed = False
else:
    print(f"[PASS] W2 Bricks correct ({expected_w2_bricks})")

if passed:
    print("\n✅ SUCCESS: Material layer verification passed.")
else:
    print("\n❌ FAILURE: Verification failed.")
