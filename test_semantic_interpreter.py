from services.semantic_interpreter import interpret_walls, normalize_to_meters

test_clean_text = """
FLOOR PLAN - LEVEL 1

Wall A 4.5m
W2 3600mm
External Wall 5.5m
HEIGHT 3.0m

DOOR 900x2100mm
WINDOW 1200x1500

Wall B 3.2m
INT 4200mm
"""

test_measurements = ["4.5m", "3600mm", "5.5m", "3.0m", "900x2100mm", "1200x1500", "3.2m", "4200mm"]
test_labels = ["FLOOR", "PLAN", "LEVEL", "WALL", "HEIGHT", "DOOR", "WINDOW", "INT"]

print("="*70)
print("PHASE 7.3.3: SEMANTIC INTERPRETATION TEST")
print("="*70)

print("\nInput Data:")
print(f"Clean Text Lines: {len(test_clean_text.split(chr(10)))}")
print(f"Measurements: {test_measurements}")
print(f"Labels: {test_labels}")

result = interpret_walls(test_clean_text, test_measurements, test_labels)

print("\nSemantic Interpretation Result:")
print(f"Walls Detected: {len(result['walls'])}")
for wall in result['walls']:
    print(f"  - {wall['label']}: {wall['length_m']}m")

print(f"\nAssumed Height: {result['assumed_wall_height_m']}m")
print(f"Confidence: {result['confidence']}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
